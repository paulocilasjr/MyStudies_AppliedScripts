#!/usr/bin/env python3
"""Generate the synthetic handoff reports through NVIDIA's hosted API and publish the viewer."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from icb_copilot.backends import build_messages
from icb_copilot.copilot import Copilot, summarize_evidence
from icb_copilot.experiment import run_experiment
from icb_copilot.handoff import prepare_handoff
from icb_copilot.handoff_export import export_handoff_bundle
from icb_copilot.io import load_jsonl
from icb_copilot.nim import DEFAULT_NIM_MODEL
from icb_copilot.prompts import PROMPT_SHA256, PROMPT_VERSION, REPLY_FIELDS
from icb_copilot.verify import verify_run


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--handoff-dir", type=Path, default=ROOT / "examples/paulo_handoff")
    parser.add_argument("--model-id", default=DEFAULT_NIM_MODEL)
    parser.add_argument("--json-mode", choices=("json_schema", "json_object", "none"), default="json_schema")
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--html-output", type=Path, default=ROOT / "exports/ICB_Patient_Explorer.html")
    return parser.parse_args()


def run(args) -> int:
    os.umask(0o077)
    run_root = (args.output_dir or ROOT / "results" / ("nim-demo-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))).resolve()
    if run_root.exists():
        raise ValueError("output root already exists; use a new directory")
    # Read and validate the current packet before any remote request. This runner
    # is intentionally restricted to the five-patient synthetic demonstration.
    prepare_handoff(args.handoff_dir, run_root / "input")
    input_path = run_root / "input/patients.jsonl"
    patients = load_jsonl(input_path)
    if not patients or any(p.data["evaluation_partition"] != "synthetic" for p in patients):
        raise ValueError("the hosted demo runner requires explicitly synthetic inputs")
    requests = []
    for record in patients:
        patient = record.to_dict()
        comparison = summarize_evidence(patient)[0]
        for field in REPLY_FIELDS:
            messages = build_messages(patient, comparison=comparison, field=field)
            digest = hashlib.sha256(json.dumps(messages, ensure_ascii=True, allow_nan=False,
                                                sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            requests.append({"patient_id": patient["patient_id"], "part": field, "messages_sha256": digest})
    contract = {"prompt_version": PROMPT_VERSION, "prompt_sha256": PROMPT_SHA256,
                "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
                "message_builder": "icb_copilot.backends.build_messages (shared with local backends)",
                "requests": requests}
    (run_root / "request_contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    print(f"Prepared {len(patients)} synthetic patients; {len(requests)} conversations using skill {PROMPT_VERSION}.", flush=True)
    print("Sending selected evidence and skill prompts to the NVIDIA hosted API.", flush=True)
    supplied_key = False
    if not os.environ.get("NVIDIA_API_KEY"):
        if not sys.stdin.isatty():
            raise ValueError("set NVIDIA_API_KEY in the environment or run interactively for a hidden prompt")
        os.environ["NVIDIA_API_KEY"] = getpass.getpass("NVIDIA API key (hidden): ").strip()
        supplied_key = True
    try:
        copilot = Copilot(backend="nim", model_id=args.model_id, max_tokens=args.max_tokens,
                          timeout=args.timeout, max_retries=args.max_retries, json_mode=args.json_mode)
        manifest = run_experiment(input_path, run_root / "experiment", copilot)
    finally:
        if supplied_key:
            os.environ.pop("NVIDIA_API_KEY", None)
    report = verify_run(input_path, run_root / "experiment", require_backend="nim",
                        require_synthetic=True, expected_model_id=args.model_id)
    print(json.dumps({"run_dir": str(run_root), "source_counts": manifest["source_counts"],
                      "verification": report["ok"], "elapsed_seconds": manifest["elapsed_seconds"]}), flush=True)
    if not report["ok"]:
        print("Report acceptance failed; review experiment/generation_review.jsonl. Existing viewer remains unchanged.", file=sys.stderr)
        return 1
    export_handoff_bundle(args.handoff_dir, run_root / "experiment", run_root / "ui")
    # Publish the self-contained HTML only after the full bundle passes export
    # validation, keeping the existing viewer intact if anything fails.
    from export_standalone_demo import export
    destination = args.html_output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".html", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        export(run_root / "ui", temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    summary = ["# NVIDIA hosted Nemotron demo", "",
               f"- Model: {args.model_id} (provider-managed revision)",
               f"- Patients: {manifest['patient_count']} synthetic records",
               f"- Sources: {manifest['source_counts']}",
               f"- Elapsed generation time: {manifest['elapsed_seconds']} s",
               f"- Skill: {PROMPT_VERSION}, SHA-256 {PROMPT_SHA256}",
               "- Verification: passed; all prose accepted by the existing heuristic screen",
               "- Original scores and features preserved; independent human review required",
               "- Uses the shared local prompt builder and skill on this input snapshot. Model and serving runtime differ, so wording can differ.",
               f"- Viewer bundle: {run_root / 'ui'}", f"- Offline HTML: {destination}", ""]
    (run_root / "SUMMARY.md").write_text("\n".join(summary))
    print(f"Updated offline viewer: {destination}\nUI bundle: {run_root / 'ui'}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run(arguments()))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"NIM demo: {exc}", file=sys.stderr)
        raise SystemExit(2)
