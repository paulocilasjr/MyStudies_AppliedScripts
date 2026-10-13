"""Exercise HPC orchestration without SLURM, conda downloads, or a GPU.

The stub Python records invocations; core inference/doctor behavior is tested
separately. These tests verify the shell's sequencing, argument preservation,
offline boundary, and setup-state handling on both laptop Bash and HPC Bash.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash"), "Bash is required for the HPC runner")
class HPCRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="copilot runner ")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.project = self.directory / "project with spaces"
        self.project.mkdir()
        shutil.copytree(PROJECT_ROOT / "scripts", self.project / "scripts")
        for filename in ("run_hpc.sh", "requirements-vllm.txt"):
            shutil.copy2(PROJECT_ROOT / filename, self.project / filename)
        (self.project / "config").mkdir()
        self.stub_directory = self.directory / "fake tools"
        self.stub_directory.mkdir()
        # Ensure /usr/bin/env python3 invokes this test suite's interpreter,
        # including when the suite uses a bundled runtime outside ordinary PATH.
        (self.stub_directory / "python3").symlink_to(sys.executable)
        self.capture = self.directory / "calls.jsonl"
        self.environment = os.environ.copy()
        self.environment.update(
            PATH=str(self.stub_directory) + os.pathsep + os.environ.get("PATH", ""),
            COPILOT_TEST_CAPTURE=str(self.capture),
        )
        # Never inherit a real site's exported module/conda shell functions or
        # shell init files; preparation must remain entirely inside the stubs.
        for variable in list(self.environment):
            if variable.startswith(("HPC_", "BASH_FUNC_")) or variable in ("BASH_ENV", "ENV"):
                self.environment.pop(variable, None)
        for variable in (
            "SLURM_JOB_ID", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE",
            "HPC_ENV_PREFIX", "HPC_MODEL_PATH", "HPC_MODEL_CACHE",
            "HPC_MODEL_ID", "HPC_MODEL_REVISION", "HPC_MODULE_INIT",
            "HPC_LOG_DIR", "HPC_ACCOUNT", "HPC_QOS",
        ):
            self.environment.pop(variable, None)

        self.make_stub("uname", "print('Linux' if args[0] == '-s' else 'x86_64')")
        self.make_stub("getconf", "print('glibc ' + os.environ.get('COPILOT_TEST_GLIBC', '2.34'))")
        self.make_stub("module", "record('module')")
        self.make_stub("sha256sum", "import hashlib; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest() + '  -')")
        self.make_stub("sbatch", "record('sbatch'); print(os.environ.get('COPILOT_TEST_JOB_RESPONSE', '54321;testcluster'))")
        self.environment_python = self.directory / "environment python stub"
        self.write_stub(
            self.environment_python,
            """record('python')
if args[:3] == ['-m', 'pip', 'freeze']:
    print('vllm==0.10.2')
if args[:3] == ['-m', 'nemotron_copilot', 'doctor']:
    sys.exit(int(os.environ.get('COPILOT_TEST_DOCTOR_STATUS', '0')))
if args[:3] == ['-m', 'nemotron_copilot', 'experiment']:
    sys.exit(int(os.environ.get('COPILOT_TEST_EXPERIMENT_STATUS', '0')))
if args[:3] == ['-m', 'nemotron_copilot', 'verify-run']:
    sys.exit(int(os.environ.get('COPILOT_TEST_VERIFICATION_STATUS', '0')))
if args[:3] == ['-m', 'nemotron_copilot', 'prepare-model']:
    snapshot = Path(args[args.index('--cache-dir') + 1]) / 'fake model snapshot'
    snapshot.mkdir(parents=True, exist_ok=True)
    (snapshot / 'config.json').write_text('{}', encoding='utf-8')
    print(snapshot)
""",
        )
        self.environment["COPILOT_TEST_PYTHON_STUB"] = str(self.environment_python)
        self.make_stub(
            "conda",
            """record('conda')
prefix = Path(args[args.index('--prefix') + 1])
(prefix / 'bin').mkdir(parents=True)
shutil.copy2(os.environ['COPILOT_TEST_PYTHON_STUB'], prefix / 'bin' / 'python')
""",
        )

    def write_stub(self, path, body):
        prelude = """#!/usr/bin/env python3
import json, os, shutil, sys
from pathlib import Path
args = sys.argv[1:]
def record(kind):
    with open(os.environ['COPILOT_TEST_CAPTURE'], 'a', encoding='utf-8') as stream:
        stream.write(json.dumps({
            'kind': kind,
            'args': args,
            'offline': os.environ.get('HF_HUB_OFFLINE'),
            'telemetry': os.environ.get('VLLM_NO_USAGE_STATS'),
        }) + '\\n')
"""
        path.write_text(prelude + body + "\n", encoding="utf-8")
        path.chmod(0o755)

    def make_stub(self, name, body):
        self.write_stub(self.stub_directory / name, body)

    def run_runner(self, *arguments, job_id=None, extra_environment=None):
        environment = self.environment.copy()
        if job_id is not None:
            environment["SLURM_JOB_ID"] = str(job_id)
        environment.update(extra_environment or {})
        return subprocess.run(
            ["bash", str(self.project / "run_hpc.sh"), *map(str, arguments)],
            cwd=self.directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def calls(self):
        if not self.capture.exists():
            return []
        return [json.loads(line) for line in self.capture.read_text(encoding="utf-8").splitlines()]

    def assert_succeeded(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def prepare(self):
        self.assert_succeeded(self.run_runner("--prepare-only"))

    def test_default_submission_preserves_empty_arguments_and_shared_paths(self):
        self.assert_succeeded(self.run_runner())
        submission = self.calls()[-1]
        self.assertEqual(submission["kind"], "sbatch")
        self.assertIn(str(self.project), submission["args"])
        self.assertIn(str(self.project / "scripts" / "hpc_job.sh"), submission["args"])
        self.assertEqual((self.project / ".state" / "last_job_id").read_text().strip(), "54321")
        self.assertIn(str(self.project / "logs" / "slurm-%j.out"), submission["args"])
        self.assertIn(str(self.project / "logs" / "slurm-%j.err"), submission["args"])

    def test_submission_preserves_paths_and_literal_shell_text(self):
        literal = "inputs/patient data;$(touch unintended).jsonl"
        self.assert_succeeded(self.run_runner("--input", literal, "--", "--max-tokens", "123"))
        arguments = self.calls()[-1]["args"]
        self.assertIn(literal, arguments)
        self.assertEqual(arguments[-3:], ["--", "--max-tokens", "123"])
        self.assertFalse((self.project / "unintended").exists())
        self.assertFalse((self.directory / "unintended").exists())

    def test_public_preparation_does_not_run_patient_inference(self):
        self.prepare()
        calls = self.calls()
        self.assertTrue(any(call["kind"] == "conda" for call in calls))
        preparations = [call for call in calls if call["args"][:3] == ["-m", "nemotron_copilot", "prepare-model"]]
        self.assertEqual(len(preparations), 1)
        self.assertIn("791833e92ebddb0bc2c1007f6d2b6764f886a2ae", preparations[0]["args"])
        self.assertFalse(any(call["args"][:3] == ["-m", "nemotron_copilot", "experiment"] for call in calls))

    def test_offline_reuse_runs_doctor_then_experiment_without_downloads(self):
        self.prepare()
        previous_count = len(self.calls())
        literal = "inputs/patient data;$(touch unintended).jsonl"
        self.assert_succeeded(self.run_runner(
            "--direct", "--offline", "--input", literal,
            "--output-dir", "output with spaces", "--", "--max-tokens", "123", job_id=99,
        ))
        calls = self.calls()[previous_count:]
        self.assertFalse(any(call["kind"] == "conda" for call in calls))
        self.assertFalse(any(call["args"][:2] == ["-m", "pip"] for call in calls))
        self.assertFalse(any(call["args"][:3] == ["-m", "nemotron_copilot", "prepare-model"] for call in calls))
        application_calls = [call for call in calls if call["args"][:2] == ["-m", "nemotron_copilot"]]
        self.assertEqual([call["args"][2] for call in application_calls], ["doctor", "experiment"])
        experiment = application_calls[-1]
        self.assertEqual(experiment["offline"], "1")
        self.assertEqual(experiment["telemetry"], "1")
        self.assertIn(literal, experiment["args"])
        self.assertIn("output with spaces", experiment["args"])
        self.assertEqual(experiment["args"][-2:], ["--max-tokens", "123"])

    def test_gpu_doctor_failure_precedes_model_download_and_cleans_lock(self):
        result = self.run_runner("--direct", job_id=99, extra_environment={"COPILOT_TEST_DOCTOR_STATUS": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any(call["args"][:3] == ["-m", "nemotron_copilot", "doctor"] for call in self.calls()))
        self.assertFalse(any(call["args"][:3] == ["-m", "nemotron_copilot", "prepare-model"] for call in self.calls()))
        self.assertFalse((self.project / ".envs" / "nemotron-vllm.setup-lock").exists())

    def test_doctor_command_skips_model_download(self):
        self.assert_succeeded(self.run_runner("--direct", "--command", "doctor", job_id=99))
        self.assertFalse(any(call["args"][:3] == ["-m", "nemotron_copilot", "prepare-model"] for call in self.calls()))
        self.assertEqual(self.calls()[-1]["args"], ["-m", "nemotron_copilot", "doctor", "--backend", "vllm"])

    def test_offline_changed_fingerprint_requires_online_preparation(self):
        self.prepare()
        previous_count = len(self.calls())
        requirements = self.project / "requirements-vllm.txt"
        requirements.write_text(requirements.read_text() + "\n# changed\n", encoding="utf-8")
        result = self.run_runner("--direct", "--offline", job_id=99)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fingerprint changed", result.stderr)
        self.assertFalse(any(call["args"][:2] == ["-m", "pip"] for call in self.calls()[previous_count:]))
        self.assertFalse((self.project / ".envs" / "nemotron-vllm.setup-lock").exists())

    def test_existing_setup_lock_is_preserved(self):
        lock = self.project / ".envs" / "nemotron-vllm.setup-lock"
        lock.mkdir(parents=True)
        (lock / "owner").write_text("another setup\n", encoding="utf-8")
        result = self.run_runner("--prepare-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Setup lock exists", result.stderr)
        self.assertEqual((lock / "owner").read_text(), "another setup\n")

    def test_old_glibc_rejected_before_environment_download(self):
        result = self.run_runner("--prepare-only", extra_environment={"COPILOT_TEST_GLIBC": "2.17"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("glibc 2.17 is too old", result.stderr)
        self.assertFalse(any(call["kind"] == "conda" for call in self.calls()))

    def test_direct_mode_requires_a_slurm_allocation(self):
        result = self.run_runner("--direct")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing SLURM GPU allocation", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_local_runner_defaults_to_mock_without_environment_bootstrap(self):
        environment = self.environment.copy()
        environment["COPILOT_PYTHON"] = str(self.environment_python)
        result = subprocess.run(
            ["bash", str(self.project / "scripts" / "run_local.sh")],
            cwd=self.directory, env=environment, capture_output=True, text=True, timeout=30,
        )
        self.assert_succeeded(result)
        self.assertEqual(len(self.calls()), 1)
        call = self.calls()[0]
        self.assertEqual(call["args"][:5], ["-m", "nemotron_copilot", "experiment", "--backend", "mock"])
        self.assertIn("examples/mock_predictions.jsonl", call["args"])
        self.assertEqual(call["offline"], "1")

    def test_gpu_smoke_generates_then_verifies_the_same_synthetic_run(self):
        self.prepare()
        previous_count = len(self.calls())
        result = self.run_runner(
            "--direct", "--offline", "--smoke", "--output-dir", "smoke output with spaces",
            "--", "--max-tokens", "300", "--batch-size=4", job_id=99,
        )
        self.assert_succeeded(result)
        calls = [call for call in self.calls()[previous_count:]
                 if call["args"][:2] == ["-m", "nemotron_copilot"]]
        self.assertEqual([call["args"][2] for call in calls], ["doctor", "experiment", "verify-run"])
        for call in calls[1:]:
            self.assertIn("examples/mock_predictions.jsonl", call["args"])
            self.assertIn("smoke output with spaces", call["args"])
            self.assertEqual(call["offline"], "1")
        self.assertIn("--backend", calls[1]["args"])
        self.assertIn("vllm", calls[1]["args"])
        self.assertIn("--require-vllm", calls[2]["args"])
        self.assertIn("--require-synthetic", calls[2]["args"])
        self.assertIn("--expected-model-id", calls[2]["args"])
        self.assertIn("nvidia/Nemotron-Mini-4B-Instruct", calls[2]["args"])
        self.assertIn("--expected-model-revision", calls[2]["args"])
        self.assertIn("791833e92ebddb0bc2c1007f6d2b6764f886a2ae", calls[2]["args"])
        self.assertIn("GPU smoke verification passed", result.stdout)

    def test_gpu_smoke_default_output_distinguishes_real_gpu_acceptance(self):
        self.prepare()
        result = self.run_runner("--direct", "--offline", "--smoke", job_id=99)
        self.assert_succeeded(result)
        self.assertIn("results/gpu-smoke-99", self.calls()[-1]["args"])

    def test_gpu_smoke_verifier_uses_configured_model_identity(self):
        revision = "a" * 40
        (self.project / "config" / "hpc.env").write_text(
            'HPC_MODEL_ID="approved/example-model"\nHPC_MODEL_REVISION="' + revision + '"\n',
            encoding="utf-8",
        )
        self.prepare()
        result = self.run_runner("--direct", "--offline", "--smoke", job_id=99)
        self.assert_succeeded(result)
        arguments = self.calls()[-1]["args"]
        self.assertEqual(arguments[arguments.index("--expected-model-id") + 1], "approved/example-model")
        self.assertEqual(arguments[arguments.index("--expected-model-revision") + 1], revision)

    def test_gpu_smoke_rejects_patient_input_and_hidden_argparse_overrides(self):
        for arguments in (
            ("--smoke", "--input", "patient.jsonl"),
            ("--smoke", "--command", "serve"),
            ("--smoke", "--prepare-only"),
            ("--smoke", "--", "--backend", "mock"),
            ("--smoke", "--", "--inp", "patient.jsonl"),
            ("--smoke", "--", "--output-dir=other"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_runner(*arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--smoke", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_gpu_smoke_stops_on_experiment_failure_before_verification(self):
        self.prepare()
        previous_count = len(self.calls())
        result = self.run_runner("--direct", "--offline", "--smoke", job_id=99,
                                 extra_environment={"COPILOT_TEST_EXPERIMENT_STATUS": "2"})
        self.assertEqual(result.returncode, 2)
        self.assertFalse(any(call["args"][:3] == ["-m", "nemotron_copilot", "verify-run"]
                             for call in self.calls()[previous_count:]))
        self.assertNotIn("GPU smoke verification passed", result.stdout)

    def test_gpu_smoke_propagates_verification_failure(self):
        self.prepare()
        result = self.run_runner("--direct", "--offline", "--smoke", job_id=99,
                                 extra_environment={"COPILOT_TEST_VERIFICATION_STATUS": "2"})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.calls()[-1]["args"][2], "verify-run")
        self.assertNotIn("GPU smoke verification passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
