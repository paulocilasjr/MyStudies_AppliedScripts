cd /share/lab_goecks/paulo/federated-learning-model

# Locate predictions and execution receipts for this iteration only.
RUN_ROOT=sources/raw/HPC_analysis_new/memory_fix_20261019T143329Z

find "$RUN_ROOT" -type f \( \
  -name 'predictions.tsv' -o \
  -name 'completion_receipt.json' -o \
  -name 'validation_report.json' -o \
  -name 'preflight_receipt.json' -o \
  -name 'interval_receipt.json' \
\) -print

# Export receipt checksums, selected completion counts, and aggregate tables.
# Original predictions and receipts remain private.
python3 - <<'PY'
import csv
import hashlib
import json
import shutil
from pathlib import Path

tag = "memory_fix_20261019T143329Z"
root = Path("sources/raw/HPC_analysis_new") / tag
dest = Path("HPC_analysis_new/results") / tag / "verification"
dest.mkdir(parents=True, exist_ok=True)

receipt_names = {
    "completion_receipt.json",
    "validation_report.json",
    "preflight_receipt.json",
    "interval_receipt.json",
}
count_fields = {
    "completed_fits", "completed_final_fits", "foundation_runs",
    "downstream_models_including_R", "task_count",
    "bootstrap_replicates", "bootstrap_seed",
}
records = []
private_locations = []
prediction_count = 0

for path in sorted(root.rglob("*")):
    if not path.is_file():
        continue

    if path.name == "predictions.tsv":
        prediction_count += 1
        private_locations.append(str(path.resolve()))
        continue

    if path.name not in receipt_names:
        continue

    data = json.loads(path.read_text())
    record = {
        "record": len(records) + 1,
        "receipt_type": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }

    status = data.get("status")
    if status in {"complete", "pass", "fail", "failed", "incomplete"}:
        record["status"] = status

    for field in count_fields:
        value = data.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            record[field] = value

    records.append(record)
    private_locations.append(str(path.resolve()))

if not records:
    raise SystemExit("No receipts found. Nothing ready to commit.")

(dest / "receipt_summary.json").write_text(
    json.dumps({
        "scope": "sanitized_receipt_inventory",
        "prediction_files_found": prediction_count,
        "predictions_exported": False,
        "independent_prediction_recalculation_performed": False,
        "receipts": records,
    }, indent=2) + "\n"
)

# Keep the location inventory inside the Git-ignored private directory.
(root / "private_evidence_locations.txt").write_text(
    "\n".join(private_locations) + "\n"
)

aggregate_names = [
    "family_auprc_intervals.tsv",
    "family_cohort_auprc_intervals.tsv",
    "per_cohort_summary.tsv",
    "macro_metrics_by_seed.tsv",
    "probability_quality_by_family.tsv",
]

for stage in ("new_nested_LFT", "new_nested_PFT"):
    source = root / f"{stage}_launch/finalized"
    for name in aggregate_names:
        path = source / name
        if path.is_file():
            if path.stat().st_size > 5_000_000:
                raise SystemExit(f"Review unexpectedly large table: {path}")
            target = dest / stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            print(f"Exported {stage}/{name}")

print(f"Found {prediction_count} private prediction files.")
print(f"Exported summaries of {len(records)} receipts.")
print("Receipt summaries preserve reported status; they do not independently validate it.")
PY
