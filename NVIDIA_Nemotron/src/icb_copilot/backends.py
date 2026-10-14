"""Inference adapters. All heavyweight imports and GPU allocation are lazy."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
from typing import Sequence

from .prompts import FIELD_INPUTS, FIELD_PROMPTS, PROMPT_VERSION
from .report import model_payload
DEFAULT_MODEL = "nvidia/Nemotron-Mini-4B-Instruct"
DEFAULT_REVISION = "791833e92ebddb0bc2c1007f6d2b6764f886a2ae"
OFFLINE_ENVIRONMENT = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
                       "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1", "VLLM_NO_USAGE_STATS": "1", "DO_NOT_TRACK": "1",
                       "VLLM_DO_NOT_TRACK": "1", "TOKENIZERS_PARALLELISM": "false"}
# One short prose part per conversation; the application renders scores, feature lists and literature.
DEFAULT_MAX_TOKENS = 200
REPLY_SCHEMA = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"], "additionalProperties": False}
# The transformers backend forces this reply prefix in place of vLLM's JSON-schema guided decoding.
JSON_REPLY_PREFIX = '{"text": "'


def _prepared_snapshot(model_path: str) -> Path:
    path = Path(model_path).expanduser().resolve()
    if not path.is_dir() or not (path / "config.json").is_file():
        raise ValueError("a prepared local model directory containing config.json is required; use prepare-model first")
    return path


def _model_manifest(path: Path) -> dict:
    manifest_path = path / "copilot_model_manifest.json"
    return json.loads(manifest_path.read_text()) if manifest_path.exists() else {"revision": "unrecorded"}


def json_string_end(text: str) -> int | None:
    """Index of the first unescaped double quote, which closes a JSON string body."""
    escaped = False
    for index, character in enumerate(text):
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == '"':
            return index
    return None


def close_json_reply(continuation: str) -> str:
    """Rebuild the forced-prefix reply; an unterminated string stays invalid JSON for the screen."""
    end = json_string_end(continuation)
    return JSON_REPLY_PREFIX + (continuation if end is None else continuation[:end] + '"}')


def build_messages(patient: dict, *, comparison: dict, field: str) -> list[dict]:
    """One focused conversation for one report part. Ground truth, partition and patient ID are withheld."""
    payload = model_payload(patient, comparison)
    payload = {key: payload[key] for key in FIELD_INPUTS[field]}
    serialized = json.dumps(payload, ensure_ascii=True, allow_nan=False)
    # Prevent model role delimiter tokens in free text from becoming chat boundaries.
    serialized = serialized.replace("<", "\\u003c").replace(">", "\\u003e")
    return [{"role": "system", "content": FIELD_PROMPTS[field]},
            {"role": "user", "content": "Interpret the following supplied research evidence:\n" + serialized}]


class VLLMBackend:
    def __init__(self, model_path: str, *, max_tokens: int = DEFAULT_MAX_TOKENS, max_model_len: int = 4096,
                 gpu_memory_utilization: float = 0.80, seed: int = 42, temperature: float = 0.0):
        path = _prepared_snapshot(model_path)
        if not 32 <= max_tokens <= 1024 or not max_tokens < max_model_len <= 4096:
            raise ValueError("token settings must fit Nemotron-Mini's 4096-token context")
        if not 0 < gpu_memory_utilization <= 0.95 or not 0 <= temperature <= 1:
            raise ValueError("invalid GPU memory utilization or temperature")
        self.path = path
        self.settings = {"max_tokens": max_tokens, "max_model_len": max_model_len,
                         "gpu_memory_utilization": gpu_memory_utilization, "seed": seed, "temperature": temperature}
        self._llm = None
        self._generation_calls = 0
        self._generated_records = 0

    @property
    def metadata(self) -> dict:
        return {"backend": "vllm", "model_path": str(self.path), "model": _model_manifest(self.path), "settings": self.settings,
                "execution": {"model_loaded": self._llm is not None,
                              "generation_calls": self._generation_calls,
                              "generated_records": self._generated_records}}

    def _load(self):
        if self._llm is None:
            os.environ.update(OFFLINE_ENVIRONMENT)
            from vllm import LLM
            self._llm = LLM(model=str(self.path), tokenizer=str(self.path), trust_remote_code=False,
                            dtype="bfloat16", tensor_parallel_size=1, enforce_eager=True,
                            max_model_len=self.settings["max_model_len"], max_num_seqs=4,
                            gpu_memory_utilization=self.settings["gpu_memory_utilization"], seed=self.settings["seed"])
        return self._llm

    def generate(self, conversations: Sequence[list[dict]]) -> list[str]:
        llm = self._load()
        tokenizer = llm.get_tokenizer()
        prompts = [tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                   for messages in conversations]
        for prompt in prompts:
            length = len(tokenizer.encode(prompt, add_special_tokens=False))
            if length + self.settings["max_tokens"] > self.settings["max_model_len"]:
                raise ValueError("input evidence exceeds the context budget; reduce supplied features or context")
        from vllm import SamplingParams
        from vllm.sampling_params import GuidedDecodingParams
        sampling = SamplingParams(temperature=self.settings["temperature"], max_tokens=self.settings["max_tokens"],
                                  seed=self.settings["seed"], guided_decoding=GuidedDecodingParams(json=REPLY_SCHEMA))
        outputs = llm.generate(prompts, sampling, use_tqdm=False)
        texts = [output.outputs[0].text.strip() for output in outputs]
        if len(texts) != len(conversations):
            raise RuntimeError("backend output count does not match input count")
        self._generation_calls += 1
        self._generated_records += len(texts)
        return texts


class TransformersBackend:
    """The same prepared snapshot and prompt through Hugging Face Transformers.

    For laptops without CUDA/vLLM: Apple Silicon (MPS) or CPU. vLLM's guided JSON
    decoding is replaced by a forced `{"text": "` reply prefix that is closed at the
    first unescaped quote; other reply shapes still fail the screen.
    Greedy decoding at temperature 0 matches the vLLM default settings.
    """
    def __init__(self, model_path: str, *, max_tokens: int = DEFAULT_MAX_TOKENS, max_model_len: int = 4096,
                 seed: int = 42, temperature: float = 0.0, device: str = "auto"):
        path = _prepared_snapshot(model_path)
        if not 32 <= max_tokens <= 1024 or not max_tokens < max_model_len <= 4096:
            raise ValueError("token settings must fit Nemotron-Mini's 4096-token context")
        if not 0 <= temperature <= 1:
            raise ValueError("invalid temperature")
        if device not in {"auto", "mps", "cpu"}:
            raise ValueError("device must be auto, mps, or cpu")
        self.path = path
        self.settings = {"max_tokens": max_tokens, "max_model_len": max_model_len, "seed": seed,
                         "temperature": temperature, "device": device,
                         "json_constraint": "forced reply prefix; closed at first unescaped quote"}
        self._model = None
        self._tokenizer = None
        self._device = None
        self._attention = None
        self._generation_calls = 0
        self._generated_records = 0

    @property
    def metadata(self) -> dict:
        return {"backend": "transformers", "model_path": str(self.path), "model": _model_manifest(self.path),
                "settings": self.settings,
                "execution": {"model_loaded": self._model is not None, "device": self._device, "attention": self._attention,
                              "generation_calls": self._generation_calls,
                              "generated_records": self._generated_records}}

    def _load(self):
        if self._model is None:
            os.environ.update(OFFLINE_ENVIRONMENT)
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            device = self.settings["device"]
            if device == "auto":
                device = "mps" if torch.backends.mps.is_available() else "cpu"
            elif device == "mps" and not torch.backends.mps.is_available():
                raise ValueError("Apple MPS is unavailable in this PyTorch build; use device cpu")
            # With torch 2.8, MPS scaled-dot-product attention in bf16/fp16 yields only
            # <pad> tokens after the first step at this prompt's ~2.3k-token context;
            # eager attention reproduces the CPU and float32 tokens.
            attention = "eager" if device == "mps" else "sdpa"
            started = time.monotonic()
            tokenizer = AutoTokenizer.from_pretrained(self.path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(self.path, local_files_only=True, trust_remote_code=False,
                                                         torch_dtype=torch.bfloat16, low_cpu_mem_usage=True,
                                                         attn_implementation=attention)
            self._model, self._tokenizer, self._device, self._attention = model.to(device).eval(), tokenizer, device, attention
            print(f"transformers backend: model loaded on {device} ({attention} attention) in {time.monotonic() - started:.1f}s",
                  file=sys.stderr, flush=True)
        return self._model, self._tokenizer

    def generate(self, conversations: Sequence[list[dict]]) -> list[str]:
        model, tokenizer = self._load()
        import torch
        from transformers import StoppingCriteria, StoppingCriteriaList

        class ClosedString(StoppingCriteria):
            def __init__(self, start):
                self.start = start

            def __call__(self, input_ids, scores, **kwargs):
                text = tokenizer.decode(input_ids[0, self.start:], skip_special_tokens=True)
                return torch.full((input_ids.shape[0],), json_string_end(text) is not None,
                                  dtype=torch.bool, device=input_ids.device)

        # Tokenize and budget-check every prompt before spending time on generation.
        # Default special-token handling matches vLLM's tokenization of text prompts.
        encoded = [tokenizer(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                             + JSON_REPLY_PREFIX, return_tensors="pt") for messages in conversations]
        for inputs in encoded:
            if inputs["input_ids"].shape[1] + self.settings["max_tokens"] > self.settings["max_model_len"]:
                raise ValueError("input evidence exceeds the context budget; reduce supplied features or context")
        sampling = ({"do_sample": True, "temperature": self.settings["temperature"]}
                    if self.settings["temperature"] > 0 else {"do_sample": False, "temperature": None, "top_p": None, "top_k": None})
        texts = []
        for index, inputs in enumerate(encoded, 1):
            started = time.monotonic()
            torch.manual_seed(self.settings["seed"])
            inputs = inputs.to(self._device)
            start = inputs["input_ids"].shape[1]
            with torch.inference_mode():
                output = model.generate(**inputs, max_new_tokens=self.settings["max_tokens"],
                                        pad_token_id=tokenizer.eos_token_id,
                                        stopping_criteria=StoppingCriteriaList([ClosedString(start)]), **sampling)
            texts.append(close_json_reply(tokenizer.decode(output[0, start:], skip_special_tokens=True)).strip())
            # Counts and timing only; patient identifiers are never logged.
            print(f"transformers backend: reply {index}/{len(encoded)} in {time.monotonic() - started:.1f}s",
                  file=sys.stderr, flush=True)
        self._generation_calls += 1
        self._generated_records += len(texts)
        return texts
