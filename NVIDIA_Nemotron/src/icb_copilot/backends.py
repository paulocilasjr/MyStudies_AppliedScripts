"""Inference adapters. All heavyweight imports and GPU allocation are lazy."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Sequence

from .prompts import PROMPT_VERSION, SYSTEM_PROMPT
DEFAULT_MODEL = "nvidia/Nemotron-Mini-4B-Instruct"
DEFAULT_REVISION = "791833e92ebddb0bc2c1007f6d2b6764f886a2ae"

def build_messages(patient: dict, *, comparison: dict | None = None) -> list[dict]:
    # Ground truth is intentionally withheld from the LLM to avoid label leakage.
    payload = {k: patient[k] for k in ("predictions", "top_features", "clinical_context", "response_definition")}
    if comparison is not None:
        payload["comparison"] = comparison
    serialized = json.dumps(payload, ensure_ascii=True, allow_nan=False)
    # Prevent model role delimiter tokens in free text from becoming chat boundaries.
    serialized = serialized.replace("<", "\\u003c").replace(">", "\\u003e")
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Interpret the following supplied research evidence:\n" + serialized}]


class VLLMBackend:
    def __init__(self, model_path: str, *, max_tokens: int = 300, max_model_len: int = 4096,
                 gpu_memory_utilization: float = 0.80, seed: int = 42, temperature: float = 0.0):
        path = Path(model_path).expanduser().resolve()
        if not path.is_dir() or not (path / "config.json").is_file():
            raise ValueError("vLLM requires a prepared local model directory containing config.json; use prepare-model first")
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
        manifest_path = self.path / "copilot_model_manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"revision": "unrecorded"}
        return {"backend": "vllm", "model_path": str(self.path), "model": manifest, "settings": self.settings,
                "execution": {"model_loaded": self._llm is not None,
                              "generation_calls": self._generation_calls,
                              "generated_records": self._generated_records}}

    def _load(self):
        if self._llm is None:
            os.environ.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
                               "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1", "VLLM_NO_USAGE_STATS": "1", "DO_NOT_TRACK": "1",
                               "VLLM_DO_NOT_TRACK": "1", "TOKENIZERS_PARALLELISM": "false"})
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
        output_schema = {"type": "object", "properties": {"interpretation": {"type": "string"}},
                         "required": ["interpretation"], "additionalProperties": False}
        sampling = SamplingParams(temperature=self.settings["temperature"], max_tokens=self.settings["max_tokens"],
                                  seed=self.settings["seed"], guided_decoding=GuidedDecodingParams(json=output_schema))
        outputs = llm.generate(prompts, sampling, use_tqdm=False)
        texts = [output.outputs[0].text.strip() for output in outputs]
        if len(texts) != len(conversations):
            raise RuntimeError("backend output count does not match input count")
        self._generation_calls += 1
        self._generated_records += len(texts)
        return texts
