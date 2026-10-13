"""Run a batch experiment and publish a complete local set of review artifacts."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .copilot import Copilot
from .evaluate import evaluate_predictions
from .io import parse_jsonl, write_jsonl


def _json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def _markdown(text):
    escaped = str(text).replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")
    # Treat producer strings and generated prose as text, including image/link
    # syntax that could otherwise fetch remote resources in a Markdown viewer.
    for character in ("\\", "`", "*", "_", "[", "]", "!", "|", "#"):
        escaped = escaped.replace(character, "\\" + character)
    return escaped


def run_experiment(input_path: str | Path, output_dir: str | Path, copilot: Copilot, *, batch_size: int = 8) -> dict:
    if not 1 <= batch_size <= 128:
        raise ValueError("batch_size must be between 1 and 128")
    source = Path(input_path).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("output directory must be absent or empty; use a new run directory to preserve prior artifacts")
    started = datetime.now(timezone.utc)
    tic = time.monotonic()
    # Parse and fingerprint the same immutable snapshot, even if upstream later
    # rewrites its file while GPU inference is running.
    input_snapshot = source.read_bytes()
    patients = parse_jsonl(input_snapshot.decode("utf-8-sig"))
    results = []
    generation_review = []
    for index in range(0, len(patients), batch_size):
        results.extend(copilot.interpret_many(patients[index:index + batch_size], generation_review=generation_review))
    metrics = evaluate_predictions(patients)
    versions = {}
    for package in ("vllm", "torch", "transformers", "huggingface-hub"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    manifest = {"copilot_version": "0.1.0", "schema_version": "1.0", "started_at_utc": started.isoformat(),
                "elapsed_seconds": round(time.monotonic() - tic, 3), "patient_count": len(patients),
                "input_path": str(source), "input_sha256": hashlib.sha256(input_snapshot).hexdigest(),
                "backend": copilot.metadata, "batch_size": batch_size, "disagreement_threshold": copilot.disagreement_threshold,
                "runtime": {"python": platform.python_version(), "os": platform.platform(), "packages": versions},
                "source_counts": dict(Counter(r["narrative_source"] for r in results)),
                "quality_counts": dict(Counter(r["quality"]["status"] for r in results)),
                "review_required": True, "response_definitions": sorted({p.data["response_definition"] for p in patients}),
                "artifacts": ["narratives.jsonl", "narratives.csv", "report.md", "manifest.json", "metrics.json", "generation_review.jsonl"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stage artifacts next to the destination; inference failure never produces a
    # partial directory that the UI could mistake for a completed experiment.
    with tempfile.TemporaryDirectory(prefix=".copilot-run-", dir=output.parent) as temporary:
        staging = Path(temporary)
        write_jsonl(staging / "narratives.jsonl", results)
        write_jsonl(staging / "generation_review.jsonl", generation_review)
        _json(staging / "manifest.json", manifest)
        _json(staging / "metrics.json", metrics)
        with (staging / "narratives.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["patient_id", "clinical_probability", "mif_probability", "fused_probability",
                                                        "narrative_source", "review_required", "narrative", "limitations"])
            writer.writeheader()
            for result in results:
                row = {key: result[key] for key in ("patient_id", "narrative_source", "review_required", "narrative")}
                row.update({m + "_probability": result["predictions"].get(m, {}).get("probability", "") for m in ("clinical", "mif", "fused")})
                row["limitations"] = " | ".join(result["limitations"])
                # Text from producers/LLM must remain text when opened in Excel.
                writer.writerow({k: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v for k, v in row.items()})
        lines = ["# ICB copilot experiment", "", f"Backend: {copilot.backend}. Patients: {len(results)}.", "",
                 "Research interpretation only. Every narrative requires human review. Automated screening does not verify clinical correctness.", "",
                 "## Prediction evaluation", "", "See metrics.json for matched held-out comparisons; unlabeled or synthetic inputs are excluded.", ""]
        for result in results:
            lines.extend([f"## {_markdown(result['patient_id'])}", "", _markdown(result["narrative"]), "",
                          f"Source: {result['narrative_source']}; quality: {result['quality']['status']}; review required: true.", ""])
            lines.extend("- " + _markdown(limitation) for limitation in result["limitations"])
            lines.append("")
        (staging / "report.md").write_text("\n".join(lines), encoding="utf-8")
        for file in staging.iterdir():
            file.chmod(0o600)
        # Empty pre-existing directories may come from mktemp-based callers.
        if output.exists():
            output.rmdir()
        os.rename(staging, output)
        output.chmod(0o700)
    return manifest
