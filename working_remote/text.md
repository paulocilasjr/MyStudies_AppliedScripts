cd /share/lab_goecks/paulo/federated-learning-model

python3 - <<'PY'
import csv
import json
import shutil
from pathlib import Path

tag = "memory_fix_20261019T143329Z"
root = Path("sources/raw/HPC_analysis_new") / tag
dest = Path("HPC_analysis_new/results") / tag
exported = 0

training = root / "sample_objective_launch/finalized/foundation_summary.json"
if training.is_file():
    data = json.loads(training.read_text())
    if data.get("status") != "complete":
        raise SystemExit("Training summary is not complete")
    fields = [
        "arm", "seed", "status", "cumulative_pooled_anchors",
        "final_validation_context_macro_loss",
        "final_validation_row_macro_loss", "checkpoint_sha256",
    ]
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "foundation_summary.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(
            {key: row.get(key, "") for key in fields}
            for row in data["runs"]
        )
    exported += 1
    print("Exported foundation_summary.tsv")

names = [
    "family_or_fixed_checkpoint_summary.tsv",
    "family_auprc_intervals.tsv",
    "family_cohort_auprc_intervals.tsv",
    "family_fixed_cohort_macro_bootstrap.tsv",
    "family_cohort_macro_bootstrap.tsv",
    "foundation_seed_effect_summary.tsv",
    "family_vs_R_effects.tsv",
    "factorial_effects.tsv",
]

for stage in ("new_nested_LFT", "new_nested_PFT"):
    source = root / f"{stage}_launch/finalized"
    receipt = source / "completion_receipt.json"
    if not receipt.is_file():
        print(f"SKIPPED {stage}: no completion receipt")
        continue
    if json.loads(receipt.read_text()).get("status") != "complete":
        raise SystemExit(f"{stage}: experiment is not complete")
    for name in names:
        path = source / name
        if not path.is_file():
            continue
        if path.stat().st_size > 5_000_000:
            raise SystemExit(f"Review unexpectedly large table: {path}")
        target = dest / stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        exported += 1
        print(f"Exported {stage}/{name}")

if not exported:
    raise SystemExit("No results found; nothing exported")
print(f"Exported {exported} aggregate files")
PY

# Continue only if the export above finished successfully.
if [ "$?" -eq 0 ]; then
    RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z

    git add -- "$RESULTS" &&
    git diff --cached --check -- "$RESULTS" &&
    git diff --cached --stat -- "$RESULTS" &&
    git --no-pager diff --cached -- "$RESULTS" &&
    {
        printf '\nConfirm the displayed tables contain no private identifiers or paths.\n'
        read -r -p 'Commit and push these results? [y/N] ' answer
        if [ "$answer" = y ] || [ "$answer" = Y ]; then
            git commit --only \
                -m "Record new foundation training and clinical evaluation results" \
                -- "$RESULTS" &&
            git push origin main
        fi
    }
fi
