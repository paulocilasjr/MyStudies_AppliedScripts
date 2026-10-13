"""Smoke acceptance must never confuse a deterministic fallback with GPU success."""
import json
from pathlib import Path
import tempfile
import unittest

from icb_copilot.copilot import Copilot
from icb_copilot.experiment import run_experiment
from icb_copilot.verify import verify_run
from helpers import prediction


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "input.jsonl"
        patient = prediction()
        patient["evaluation_partition"] = "synthetic"
        self.source.write_text(json.dumps(patient) + "\n")
        self.output = self.root / "run"

    def generate(self, copilot=None):
        return run_experiment(self.source, self.output, copilot or Copilot(backend="mock"))

    def rewrite(self, filename, mutate):
        path = self.output / filename
        obj = json.loads(path.read_text())
        mutate(obj)
        path.write_text(json.dumps(obj) + "\n")

    def test_mock_plumbing_passes_but_cannot_pass_real_model_acceptance(self):
        self.generate()
        self.assertTrue(verify_run(self.source, self.output, require_synthetic=True)["ok"])
        result = verify_run(self.source, self.output, require_vllm=True)
        self.assertFalse(result["ok"])
        self.assertIn("local_vllm_executed", result["errors"])
        self.assertIn("all_generated_narratives_accepted", result["errors"])
        self.assertEqual((self.output / "verification.json").stat().st_mode & 0o777, 0o600)

    def test_changed_input_or_output_scores_fail(self):
        self.generate()
        original = (self.output / "narratives.jsonl").read_text()
        self.rewrite("narratives.jsonl", lambda r: r["predictions"]["clinical"].update(probability=0.1))
        result = verify_run(self.source, self.output)
        self.assertFalse(result["ok"])
        self.assertIn("invalid_run_artifact", result["errors"][0])
        (self.output / "narratives.jsonl").write_text(original)
        self.source.write_text(self.source.read_text() + "\n")
        self.assertIn("input_hash_matches", verify_run(self.source, self.output)["errors"])

    def test_missing_artifact_or_boolean_class_fails(self):
        self.generate()
        self.rewrite("narratives.jsonl", lambda r: r["comparison"]["predicted_classes"].update(clinical=True))
        self.assertFalse(verify_run(self.source, self.output)["ok"])
        (self.output / "metrics.json").unlink()
        self.assertIn("missing artifacts", verify_run(self.source, self.output)["errors"][0])

    def test_missing_or_wrong_model_identity_fails(self):
        self.generate()
        report = verify_run(self.source, self.output, expected_model_id="nvidia/Nemotron-Mini-4B-Instruct",
                            expected_model_revision="a" * 40)
        self.assertIn("expected_model_matches", report["errors"])

    def test_truncated_output_and_malformed_metadata_fail(self):
        self.generate()
        (self.output / "narratives.jsonl").write_text("")
        self.assertFalse(verify_run(self.source, self.output)["ok"])
        self.rewrite("manifest.json", lambda m: m.update(disagreement_threshold=None))
        self.assertIn("invalid_run_artifact", verify_run(self.source, self.output)["errors"][0])

    def test_injected_generator_is_not_gpu_evidence(self):
        text = json.dumps({"interpretation": "The modalities provide complementary evidence for review. Independent assessment is required."})
        self.generate(Copilot(backend="vllm", generator=lambda messages: [text] * len(messages)))
        report = verify_run(self.source, self.output, require_vllm=True)
        self.assertFalse(report["ok"])
        self.assertTrue(report["checks"]["all_generated_narratives_accepted"])
        self.assertFalse(report["checks"]["local_vllm_executed"])

    def test_fallback_fails_even_when_execution_is_recorded(self):
        self.generate(Copilot(backend="vllm", generator=lambda messages: ["bad JSON"] * len(messages)))
        self.rewrite("manifest.json", lambda m: m.update(backend={"backend": "vllm", "execution": {
            "model_loaded": True, "generation_calls": 1, "generated_records": 1}}))
        report = verify_run(self.source, self.output, require_vllm=True)
        self.assertTrue(report["checks"]["local_vllm_executed"])
        self.assertFalse(report["checks"]["all_generated_narratives_accepted"])
        self.assertFalse(report["ok"])

    def test_real_execution_metadata_with_accepted_output_passes_acceptance(self):
        # Artifact fixture only; this test does not execute vLLM or claim GPU validation.
        text = json.dumps({"interpretation": "The modalities provide complementary evidence for review. Independent assessment is required."})
        self.generate(Copilot(backend="vllm", generator=lambda messages: [text] * len(messages)))
        self.rewrite("manifest.json", lambda m: m.update(backend={"backend": "vllm", "execution": {
            "model_loaded": True, "generation_calls": 1, "generated_records": 1}}))
        self.rewrite("narratives.jsonl", lambda r: r["provenance"].pop("generator"))
        report = verify_run(self.source, self.output, require_vllm=True, require_synthetic=True)
        self.assertTrue(report["ok"], report)

    def test_real_patient_partition_fails_synthetic_requirement(self):
        patient = json.loads(self.source.read_text())
        patient["evaluation_partition"] = "test"
        self.source.write_text(json.dumps(patient) + "\n")
        self.generate()
        self.assertIn("inputs_declared_synthetic", verify_run(self.source, self.output, require_synthetic=True)["errors"])


if __name__ == "__main__":
    unittest.main()
