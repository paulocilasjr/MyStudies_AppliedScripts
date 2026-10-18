"""Hosted inference retains the local prompt/evidence and proves its own execution."""
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from helpers import generator, prediction
from icb_copilot.cli import _copilot, parser
from icb_copilot.copilot import Copilot
from icb_copilot.experiment import run_experiment
from icb_copilot.nim import DEFAULT_NIM_MODEL
from icb_copilot.verify import verify_run


class HostedIntegrationTests(unittest.TestCase):
    def opener(self, captured):
        class Opener:
            def open(self, request, timeout):
                payload = json.loads(request.data)
                captured.append(payload["messages"])
                body = {"choices": [{"finish_reason": "stop", "message": {
                    "content": generator()([payload["messages"]])[0]}}]}
                response = io.BytesIO(json.dumps(body).encode())
                response.status = 200
                return response
        return Opener()

    def test_nim_and_local_receive_identical_skill_and_evidence(self):
        local_messages, hosted_messages = [], []
        def local(conversations):
            local_messages.extend(conversations)
            return generator()(conversations)
        patient = prediction()
        patient.update(ground_truth=1, evaluation_partition="synthetic")
        expected = Copilot(backend="transformers", generator=local).interpret(patient)
        with patch.dict(os.environ, {"NVIDIA_API_KEY": "synthetic-test-token"}), \
             patch("icb_copilot.nim.build_opener", return_value=self.opener(hosted_messages)):
            actual = Copilot(backend="nim").interpret(patient)
        self.assertEqual(hosted_messages, local_messages)
        self.assertEqual(len(hosted_messages), 3)
        self.assertEqual(actual["narrative"], expected["narrative"])
        self.assertEqual(actual["predictions"], expected["predictions"])
        self.assertEqual(actual["narrative_source"], "nim")
        self.assertNotIn("synthetic-test-token", json.dumps(actual))

    def test_real_adapter_requires_three_recorded_remote_replies_for_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            patient = prediction()
            patient["evaluation_partition"] = "synthetic"
            source = root / "input.jsonl"
            source.write_text(json.dumps(patient) + "\n")
            with patch.dict(os.environ, {"NVIDIA_API_KEY": "synthetic-test-token"}), \
                 patch("icb_copilot.nim.build_opener", return_value=self.opener([])):
                copilot = Copilot(backend="nim")
                copilot.interpret(patient)  # A reusable engine has lifetime counters.
                run_experiment(source, root / "run", copilot)
            report = verify_run(source, root / "run", require_backend="nim", require_synthetic=True,
                                expected_model_id=DEFAULT_NIM_MODEL)
            self.assertTrue(report["ok"], report)
            self.assertTrue(report["checks"]["remote_nim_executed"])
            self.assertFalse(verify_run(source, root / "run", require_backend="transformers")["ok"])
            manifest_path = root / "run/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["backend"]["execution"]["remote_successes"] = 1
            manifest_path.write_text(json.dumps(manifest))
            self.assertIn("remote_nim_executed", verify_run(source, root / "run", require_backend="nim")["errors"])

    def test_nim_cli_routes_hosted_settings_without_local_snapshot(self):
        args = parser().parse_args(["experiment", "--backend", "nim", "--input", "input.jsonl",
                                    "--output-dir", "run", "--nim-json-mode", "json_object",
                                    "--nim-timeout", "60"])
        copilot = _copilot(args)
        self.assertEqual(copilot.metadata["settings"]["json_mode"], "json_object")
        self.assertEqual(copilot.metadata["settings"]["timeout"], 60)
        self.assertEqual(copilot.metadata["model"]["model_id"], DEFAULT_NIM_MODEL)
        with self.assertRaisesRegex(ValueError, "local model_path"):
            Copilot(backend="nim", model_path="some-snapshot")

    def test_nim_without_key_fails_before_request(self):
        with patch.dict(os.environ, {}, clear=True), patch("icb_copilot.nim.build_opener") as opener:
            with self.assertRaisesRegex(ValueError, "NVIDIA_API_KEY"):
                Copilot(backend="nim").interpret(prediction())
            opener.return_value.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
