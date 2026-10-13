"""Laptop smoke tests, HPC experiments, and the team's local integration API."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .backends import DEFAULT_MODEL, DEFAULT_REVISION
from .copilot import Copilot
from .experiment import run_experiment
from .io import assemble_predictions, load_jsonl, write_jsonl
from .models import doctor, prepare_model
from .server import create_server
from .verify import verify_run


def _inference_arguments(parser):
    parser.add_argument("--backend", choices=("mock", "vllm"), default="vllm")
    parser.add_argument("--model-path", help="prepared local snapshot; remote model names are not accepted")
    parser.add_argument("--max-tokens", type=int, default=300)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--disagreement-threshold", type=float, default=0.20)


def _copilot(args):
    settings = {key: getattr(args, key) for key in ("max_tokens", "max_model_len", "gpu_memory_utilization", "seed", "temperature")} if args.backend == "vllm" else {}
    return Copilot(backend=args.backend, model_path=args.model_path,
                   disagreement_threshold=args.disagreement_threshold, **settings)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Local research interpretation of multimodal ICB prediction outputs")
    commands = root.add_subparsers(dest="command", required=True)
    experiment = commands.add_parser("experiment", help="generate narratives and experiment artifacts")
    _inference_arguments(experiment)
    experiment.add_argument("--input", required=True, help="canonical patient JSONL")
    experiment.add_argument("--output-dir", required=True, help="new or empty directory; existing runs are protected")
    experiment.add_argument("--batch-size", type=int, default=8)
    verify = commands.add_parser("verify-run", help="check completed artifacts and optionally require accepted real-model output")
    verify.add_argument("--input", required=True)
    verify.add_argument("--output-dir", required=True)
    verify.add_argument("--require-vllm", action="store_true")
    verify.add_argument("--require-synthetic", action="store_true")
    verify.add_argument("--expected-model-id")
    verify.add_argument("--expected-model-revision")
    export = commands.add_parser("export-ui", help="export the file contract used by melanoma-demo-ui")
    export.add_argument("--run-dir", required=True)
    export.add_argument("--output-dir", required=True)
    export.add_argument("--input", help="optional original canonical input, hash-checked before exporting eligible ground truth")
    validate = commands.add_parser("validate", help="validate JSONL without loading any model")
    validate.add_argument("--input", required=True)
    assemble = commands.add_parser("assemble", help="join team prediction CSVs by canonical patient ID")
    for modality in ("clinical", "mif", "fused"):
        assemble.add_argument(f"--{modality}-csv")
    assemble.add_argument("--context-jsonl")
    assemble.add_argument("--output", required=True)
    prepare = commands.add_parser("prepare-model", help="download public artifacts only; no patient input")
    prepare.add_argument("--model-id", default=DEFAULT_MODEL)
    prepare.add_argument("--revision", default=DEFAULT_REVISION)
    prepare.add_argument("--cache-dir", default=".cache/huggingface/hub")
    diagnose = commands.add_parser("doctor", help="check Python, pinned runtime, GPU and driver")
    diagnose.add_argument("--backend", choices=("mock", "vllm"), default="vllm")
    serve = commands.add_parser("serve", help="loopback-only interpretation API")
    _inference_arguments(serve)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return root


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validate":
            patients = load_jsonl(args.input)
            print(json.dumps({"valid": True, "patient_count": len(patients), "schema_version": "1.0"}))
        elif args.command == "assemble":
            patients = assemble_predictions(clinical_csv=args.clinical_csv, mif_csv=args.mif_csv,
                                             fused_csv=args.fused_csv, context_jsonl=args.context_jsonl)
            destination = Path(args.output).expanduser()
            if destination.exists():
                raise ValueError("assemble output already exists; choose a new path")
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects another process's output; restrict permissions.
            with destination.open("x"):
                pass
            destination.chmod(0o600)
            write_jsonl(destination, patients)
            print(json.dumps({"patient_count": len(patients), "output": str(destination.resolve())}))
        elif args.command == "prepare-model":
            print(prepare_model(args.model_id, args.revision, args.cache_dir))
        elif args.command == "doctor":
            report = doctor(args.backend)
            print(json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
        elif args.command == "experiment":
            manifest = run_experiment(args.input, args.output_dir, _copilot(args), batch_size=args.batch_size)
            print(json.dumps({"patient_count": manifest["patient_count"], "backend": args.backend,
                              "output_dir": str(Path(args.output_dir).resolve()), "source_counts": manifest["source_counts"]}))
        elif args.command == "verify-run":
            report = verify_run(args.input, args.output_dir, require_vllm=args.require_vllm,
                                require_synthetic=args.require_synthetic, expected_model_id=args.expected_model_id,
                                expected_model_revision=args.expected_model_revision)
            print(json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
        elif args.command == "export-ui":
            from .ui_export import export_ui_bundle
            report = export_ui_bundle(args.run_dir, args.output_dir, canonical_input=args.input)
            print(json.dumps(report, indent=2))
        elif args.command == "serve":
            server = create_server(_copilot(args), args.host, args.port)
            print(f"Local {args.backend} copilot API: http://{server.server_address[0]}:{server.server_address[1]}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        return 0
    except (ValueError, OSError, ImportError) as exc:
        print(f"copilot: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
