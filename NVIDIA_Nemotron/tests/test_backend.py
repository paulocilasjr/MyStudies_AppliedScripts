"""Verify the local vLLM/Transformers adapters without installing or contacting GPU libraries."""

import contextlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from icb_copilot.backends import (JSON_REPLY_PREFIX, REPLY_SCHEMA, TransformersBackend, VLLMBackend, build_messages,
                                  close_json_reply)
from icb_copilot.copilot import summarize_evidence
from icb_copilot.models import prepare_model
from icb_copilot.prompts import FIELD_PROMPTS

from helpers import prediction


def messages(patient=None, field="prediction_summary"):
    patient = patient or prediction()
    return build_messages(patient, comparison=summarize_evidence(patient)[0], field=field)


class BackendTests(unittest.TestCase):
    def test_remote_model_name_is_not_accepted_for_inference(self):
        with self.assertRaisesRegex(ValueError, "local model"):
            VLLMBackend("nvidia/Nemotron-Mini-4B-Instruct")

    def test_lazy_model_load_uses_chat_template_offline_flags_and_reused_engine(self):
        calls = []

        class FakeTokenizer:
            def apply_chat_template(self, conversation, **settings):
                calls.append(("template", conversation, settings))
                return "Templated evidence"

            def encode(self, prompt, **settings):
                return [1] * 20

        class FakeLLM:
            def __init__(self, **settings):
                self.tokenizer = FakeTokenizer()
                calls.append(("load", settings))
                self_test.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
                self_test.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "1")
                self_test.assertEqual(os.environ["HF_HUB_DISABLE_TELEMETRY"], "1")

            def get_tokenizer(self):
                return self.tokenizer

            def generate(self, prompts, sampling, **settings):
                calls.append(("generate", prompts, sampling, settings))
                return [SimpleNamespace(outputs=[SimpleNamespace(text=' {"text":"Synthetic response"} ')]) for _ in prompts]

        self_test = self
        fake_module = SimpleNamespace(LLM=FakeLLM, SamplingParams=lambda **settings: settings)
        fake_decoding = SimpleNamespace(GuidedDecodingParams=lambda **settings: settings)
        with tempfile.TemporaryDirectory() as directory, patch.dict(sys.modules, {
            "vllm": fake_module, "vllm.sampling_params": fake_decoding,
        }), patch.dict(os.environ):
            root = Path(directory)
            (root / "config.json").write_text("{}", encoding="utf-8")
            adapter = VLLMBackend(str(root), seed=123)
            self.assertFalse(calls, "constructing an adapter must not allocate a GPU")
            self.assertEqual(adapter.metadata["execution"], {"model_loaded": False, "generation_calls": 0, "generated_records": 0})
            conversations = [messages()]
            first = adapter.generate(conversations)
            second = adapter.generate(conversations)
            self.assertEqual(adapter.metadata["execution"], {"model_loaded": True, "generation_calls": 2, "generated_records": 2})
            self.assertEqual(first, second)
            self.assertEqual(first, ['{"text":"Synthetic response"}'])
            self.assertEqual(len([call for call in calls if call[0] == "load"]), 1)
            loader = next(call[1] for call in calls if call[0] == "load")
            self.assertEqual(loader["model"], str(root.resolve()))
            self.assertEqual(loader["tokenizer"], str(root.resolve()))
            self.assertEqual(loader["dtype"], "bfloat16")
            self.assertEqual(loader["tensor_parallel_size"], 1)
            self.assertFalse(loader["trust_remote_code"])
            template = next(call for call in calls if call[0] == "template")
            self.assertEqual(template[2], {"tokenize": False, "add_generation_prompt": True})
            sampling = next(call[2] for call in calls if call[0] == "generate")
            self.assertEqual(sampling["seed"], 123)
            self.assertEqual(sampling["temperature"], 0.0)
            self.assertEqual(sampling["guided_decoding"]["json"], {
                "type": "object", "properties": {"text": {"type": "string"}},
                "required": ["text"], "additionalProperties": False})
            self.assertEqual(sampling["guided_decoding"]["json"], REPLY_SCHEMA)
            self.assertEqual(sampling["max_tokens"], 200)

    def test_each_report_part_has_its_own_focused_prompt(self):
        patient = prediction()
        for field, prompt in FIELD_PROMPTS.items():
            with self.subTest(field=field):
                conversation = messages(patient, field)
                self.assertEqual(conversation[0]["content"], prompt)
                payload = json.loads(conversation[1]["content"].split("\n", 1)[1])
                expected = {"prediction_summary": {"situation", "hypothesis"}, "clinical_interpretation": {"clinical_evidence"},
                            "conclusion": {"situation", "hypothesis"}}[field]
                self.assertEqual(set(payload), expected)

    def test_context_budget_is_checked_before_model_generation(self):
        generated = []
        tokenizer = SimpleNamespace(
            apply_chat_template=lambda *args, **kwargs: "Templated evidence",
            encode=lambda *args, **kwargs: [1] * 4000,
        )
        engine = SimpleNamespace(
            get_tokenizer=lambda: tokenizer,
            generate=lambda *args, **kwargs: generated.append(True),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text(json.dumps({}), encoding="utf-8")
            adapter = VLLMBackend(str(root))
            adapter._llm = engine
            with self.assertRaisesRegex(ValueError, "context budget"):
                adapter.generate([messages()])
            self.assertFalse(generated)


class TransformersBackendTests(unittest.TestCase):
    def snapshot(self, directory):
        root = Path(directory)
        (root / "config.json").write_text("{}", encoding="utf-8")
        return root

    def test_forced_reply_is_closed_only_at_an_unescaped_quote(self):
        self.assertEqual(close_json_reply('Two sentences."} trailing'), '{"text": "Two sentences."}')
        self.assertEqual(json.loads(close_json_reply('Quoted \\"term\\" kept." more'))["text"], 'Quoted "term" kept.')
        # An unterminated reply stays invalid JSON so the screen falls back.
        with self.assertRaises(ValueError):
            json.loads(close_json_reply("never closed"))

    def test_remote_model_names_and_unknown_devices_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "local model"):
            TransformersBackend("nvidia/Nemotron-Mini-4B-Instruct")
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, "device"):
            TransformersBackend(str(self.snapshot(directory)), device="cuda")

    def fake_runtime(self, calls, prompt_tokens=20, continuation='Synthetic response."} ignored'):
        test = self

        class Encoding(dict):
            def to(self, device):
                calls.append(("to", device))
                return self

        class Tokenizer:
            eos_token_id = 3

            def apply_chat_template(self, conversation, **settings):
                calls.append(("template", settings))
                return "Templated evidence\n"

            def __call__(self, text, **settings):
                calls.append(("tokenize", text, settings))
                return Encoding(input_ids=SimpleNamespace(shape=(1, prompt_tokens)))

            def decode(self, tokens, **settings):
                return continuation

        class Model:
            def to(self, device):
                calls.append(("device", device))
                return self

            def eval(self):
                return self

            def generate(self, **settings):
                calls.append(("generate", settings))
                return {(0, slice(prompt_tokens, None)): "generated tokens"}

        def load_model(path, **settings):
            calls.append(("load", path, settings))
            test.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
            test.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "1")
            return Model()

        torch = SimpleNamespace(backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda: True)),
                                bfloat16="bfloat16", manual_seed=lambda seed: calls.append(("seed", seed)),
                                inference_mode=contextlib.nullcontext)
        transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda path, **settings: Tokenizer()),
                                       AutoModelForCausalLM=SimpleNamespace(from_pretrained=load_model),
                                       StoppingCriteria=object, StoppingCriteriaList=list)
        return patch.dict(sys.modules, {"torch": torch, "transformers": transformers})

    def test_lazy_offline_load_forced_prefix_and_greedy_generation(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory, self.fake_runtime(calls), patch.dict(os.environ):
            root = self.snapshot(directory)
            adapter = TransformersBackend(str(root), seed=7)
            self.assertFalse(calls, "constructing an adapter must not load the model")
            self.assertEqual(adapter.metadata["execution"]["model_loaded"], False)
            conversations = [messages()]
            first = adapter.generate(conversations)
            self.assertEqual(first, adapter.generate(conversations))
            self.assertEqual(first, ['{"text": "Synthetic response."}'])
            self.assertEqual(len([call for call in calls if call[0] == "load"]), 1)
            loader = next(call for call in calls if call[0] == "load")
            self.assertEqual(loader[1], root.resolve())
            self.assertEqual(loader[2]["torch_dtype"], "bfloat16")
            self.assertTrue(loader[2]["local_files_only"])
            self.assertFalse(loader[2]["trust_remote_code"])
            self.assertEqual(loader[2]["attn_implementation"], "eager")
            self.assertIn(("device", "mps"), calls)
            prompt = next(call for call in calls if call[0] == "tokenize")
            self.assertEqual(prompt[1], "Templated evidence\n" + JSON_REPLY_PREFIX)
            template = next(call for call in calls if call[0] == "template")
            self.assertEqual(template[1], {"tokenize": False, "add_generation_prompt": True})
            generation = next(call[1] for call in calls if call[0] == "generate")
            self.assertFalse(generation["do_sample"])
            self.assertEqual(generation["max_new_tokens"], 200)
            self.assertIn(("seed", 7), calls)
            self.assertEqual(adapter.metadata["backend"], "transformers")
            self.assertEqual(adapter.metadata["execution"], {"model_loaded": True, "device": "mps", "attention": "eager",
                                                             "generation_calls": 2, "generated_records": 2})

    def test_context_budget_is_checked_before_generation(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory, self.fake_runtime(calls, prompt_tokens=4000), patch.dict(os.environ):
            adapter = TransformersBackend(str(self.snapshot(directory)))
            with self.assertRaisesRegex(ValueError, "context budget"):
                adapter.generate([messages()])
            self.assertFalse([call for call in calls if call[0] == "generate"])


class ModelPreparationTests(unittest.TestCase):
    def fake_hub(self, snapshot, calls):
        def download(**settings):
            calls.append(settings)
            return str(snapshot)

        return patch.dict(sys.modules, {
            "huggingface_hub": SimpleNamespace(snapshot_download=download),
            "huggingface_hub.utils": SimpleNamespace(disable_progress_bars=lambda: None),
        })

    def test_binary_checkpoint_is_downloaded_and_its_revision_is_recorded(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ):
            root = Path(directory)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            (snapshot / "config.json").write_text("{}", encoding="utf-8")
            (snapshot / "tokenizer_config.json").write_text("{}", encoding="utf-8")
            (snapshot / "pytorch_model.bin").write_bytes(b"Synthetic weight fixture")
            with self.fake_hub(snapshot, calls):
                result = prepare_model("synthetic/model", "a" * 40, str(root / "cache"))
            self.assertEqual(result, str(snapshot.resolve()))
            self.assertIn("pytorch_model*.bin", calls[0]["allow_patterns"])
            self.assertFalse(calls[0]["token"])
            manifest = json.loads((snapshot / "copilot_model_manifest.json").read_text())
            self.assertEqual(manifest["revision"], "a" * 40)
            self.assertEqual(manifest["weight_files"][0]["name"], "pytorch_model.bin")
            self.assertGreater(manifest["weight_files"][0]["bytes"], 0)

    def test_missing_sharded_weights_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ):
            root = Path(directory)
            (root / "config.json").write_text("{}", encoding="utf-8")
            (root / "tokenizer_config.json").write_text("{}", encoding="utf-8")
            (root / "model.safetensors.index.json").write_text(json.dumps({
                "weight_map": {"weight_a": "part-a.safetensors", "weight_b": "part-b.safetensors"}
            }), encoding="utf-8")
            (root / "part-a.safetensors").write_bytes(b"Synthetic shard fixture")
            with self.fake_hub(root, []), self.assertRaisesRegex(ValueError, "incomplete"):
                prepare_model("synthetic/model", "b" * 40, str(root / "cache"))

    def test_mutable_model_revision_is_rejected_before_download(self):
        with self.assertRaisesRegex(ValueError, "exact.*commit hash"):
            prepare_model("synthetic/model", "main")


if __name__ == "__main__":
    unittest.main()
