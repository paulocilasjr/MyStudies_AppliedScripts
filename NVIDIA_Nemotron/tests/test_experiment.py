"""Experiments must preserve prior runs and publish reviewable complete artifacts."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from nemotron_copilot import Copilot
from icb_copilot.experiment import run_experiment

from helpers import generator as part_generator, prediction


class ExperimentTests(unittest.TestCase):
    def write_input(self, root):
        path = root / "patients.jsonl"
        path.write_text(json.dumps(prediction()) + "\n", encoding="utf-8")
        return path

    def test_complete_artifacts_preserve_input_hash_and_mock_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.write_input(root)
            output = root / "results"
            manifest = run_experiment(source, output, Copilot(backend="mock"))
            self.assertEqual(manifest["input_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(manifest["source_counts"], {"mock": 1})
            self.assertEqual(set(manifest["artifacts"]), {path.name for path in output.iterdir()})
            self.assertEqual(json.loads((output / "metrics.json").read_text())["groups"], [])
            self.assertEqual(output.stat().st_mode & 0o777, 0o700)
            self.assertTrue(all(path.stat().st_mode & 0o777 == 0o600 for path in output.iterdir()))

    def test_existing_runs_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.write_input(root)
            output = root / "results"
            output.mkdir()
            prior = output / "prior.txt"
            prior.write_text("Already reviewed output", encoding="utf-8")
            with self.assertRaises(ValueError):
                run_experiment(source, output, Copilot(backend="mock"))
            self.assertEqual(prior.read_text(encoding="utf-8"), "Already reviewed output")

    def test_inference_failure_does_not_publish_partial_results(self):
        def fail(conversations):
            raise RuntimeError("Synthetic backend failure")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.write_input(root)
            output = root / "results"
            with self.assertRaises(RuntimeError):
                run_experiment(source, output, Copilot(backend="vllm", generator=fail))
            self.assertFalse(output.exists())
            self.assertFalse(list(root.glob(".copilot-run-*")))

    def test_manifest_hash_describes_the_consumed_input_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.write_input(root)
            output = root / "results"
            original_hash = hashlib.sha256(source.read_bytes()).hexdigest()

            def generator(conversations):
                changed = prediction()
                changed["predictions"]["clinical"]["probability"] = 0.1
                source.write_text(json.dumps(changed) + "\n", encoding="utf-8")
                return part_generator()(conversations)

            manifest = run_experiment(source, output, Copilot(backend="vllm", generator=generator))
            self.assertEqual(manifest["input_sha256"], original_hash)
            self.assertNotEqual(manifest["input_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            row = json.loads((output / "narratives.jsonl").read_text())
            self.assertEqual(row["predictions"]["clinical"]["probability"], 0.85)


if __name__ == "__main__":
    unittest.main()
