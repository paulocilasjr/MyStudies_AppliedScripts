"""Verify the local vLLM adapter without installing or contacting GPU libraries."""

import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from icb_copilot.backends import VLLMBackend, build_messages
from icb_copilot.models import prepare_model

from helpers import prediction


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
                return [SimpleNamespace(outputs=[SimpleNamespace(text=' {"interpretation":"Synthetic response"} ')]) for _ in prompts]

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
            conversations = [build_messages(prediction())]
            first = adapter.generate(conversations)
            second = adapter.generate(conversations)
            self.assertEqual(first, second)
            self.assertEqual(first, ['{"interpretation":"Synthetic response"}'])
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
                "type": "object", "properties": {"interpretation": {"type": "string"}},
                "required": ["interpretation"], "additionalProperties": False,
            })

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
                adapter.generate([build_messages(prediction())])
            self.assertFalse(generated)


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
