"""Exercise the handoff CLI in a fresh, dependency-free process."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from helpers import clinical_only, prediction


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *arguments):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "nemotron_copilot", *map(str, arguments)],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_validate_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "duplicates.jsonl"
            source = json.dumps(prediction()).replace(
                '"patient_id": "P48"', '"patient_id": "P48", "patient_id": "P99"'
            )
            input_path.write_text(source + "\n", encoding="utf-8")
            result = self.run_cli("validate", "--input", input_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", (result.stdout + result.stderr).lower())

    def test_validate_rejects_duplicate_patient_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "duplicate_patients.jsonl"
            input_path.write_text(
                json.dumps(prediction()) + "\n" + json.dumps(prediction()) + "\n", encoding="utf-8"
            )
            result = self.run_cli("validate", "--input", input_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", (result.stdout + result.stderr).lower())

    def test_validate_reports_bad_line_without_running_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "invalid.jsonl"
            invalid = prediction()
            invalid["predictions"]["clinical"]["probability"] = 2.5
            input_path.write_text(json.dumps(prediction()) + "\n" + json.dumps(invalid) + "\n", encoding="utf-8")
            result = self.run_cli("validate", "--input", input_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("2", result.stdout + result.stderr)
            self.assertNotIn("ModuleNotFoundError", result.stderr)

    def test_mock_experiment_produces_one_narrative_per_patient_in_input_order(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            input_path = temporary_root / "patients.jsonl"
            patients = [prediction("P48"), clinical_only("P07")]
            input_path.write_text("\n".join(map(json.dumps, patients)) + "\n", encoding="utf-8")
            output_dir = temporary_root / "experiment"
            result = self.run_cli("experiment", "--input", input_path, "--output-dir", output_dir, "--backend", "mock")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            narrative_files = list(output_dir.glob("*narrative*.jsonl"))
            self.assertEqual(len(narrative_files), 1)
            rows = [json.loads(line) for line in narrative_files[0].read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["patient_id"] for row in rows], ["P48", "P07"])
            for row in rows:
                self.assertIsInstance(row["narrative"], str)
                self.assertTrue(row["narrative"].strip())

    def test_mock_mode_does_not_import_gpu_libraries(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        code = (
            "import json, sys; from nemotron_copilot import Copilot; "
            f"c = Copilot(backend='mock'); c.interpret(json.loads({json.dumps(json.dumps(clinical_only()))})); "
            "assert not any(name in sys.modules for name in ('vllm', 'torch', 'transformers', 'huggingface_hub'))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=PROJECT_ROOT, env=environment,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
