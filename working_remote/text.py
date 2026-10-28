(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
ort shutil
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
            g(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
it push origin main
        fi
    }
fi(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ python3 - <<'PY'
> import csv
> import json
> import shutil
> from pathlib import Path
>
> tag = "memory_fix_20261019T143329Z"
> root = Path("sources/raw/HPC_analysis_new") / tag
> dest = Path("HPC_analysis_new/results") / tag
> exported = 0
>
> training = root / "sample_objective_launch/finalized/foundation_summary.json"
> if training.is_file():
>     data = json.loads(training.read_text())
>     if data.get("status") != "complete":
>         raise SystemExit("Training summary is not complete")
>     fields = [
>         "arm", "seed", "status", "cumulative_pooled_anchors",
>         "final_validation_context_macro_loss",
>         "final_validation_row_macro_loss", "checkpoint_sha256",
>     ]
>     dest.mkdir(parents=True, exist_ok=True)
>     with (dest / "foundation_summary.tsv").open("w", newline="") as handle:
>         writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
>         writer.writeheader()
>         writer.writerows(
>             {key: row.get(key, "") for key in fields}
>             for row in data["runs"]
>         )
>     exported += 1
>     print("Exported foundation_summary.tsv")
>
> names = [
>     "family_or_fixed_checkpoint_summary.tsv",
>     "family_auprc_intervals.tsv",
>     "family_cohort_auprc_intervals.tsv",
>     "family_fixed_cohort_macro_bootstrap.tsv",
>     "family_cohort_macro_bootstrap.tsv",
>     "foundation_seed_effect_summary.tsv",
>     "family_vs_R_effects.tsv",
>     "factorial_effects.tsv",
> ]
>
> for stage in ("new_nested_LFT", "new_nested_PFT"):
>     source = root / f"{stage}_launch/finalized"
>     receipt = source / "completion_receipt.json"
>     if not receipt.is_file():
>         print(f"SKIPPED {stage}: no completion receipt")
>         continue
>     if json.loads(receipt.read_text()).get("status") != "complete":
>         raise SystemExit(f"{stage}: experiment is not complete")
>     for name in names:
>         path = source / name
>         if not path.is_file():
>             continue
>         if path.stat().st_size > 5_000_000:
>             raise SystemExit(f"Review unexpectedly large table: {path}")
>         target = dest / stage / name
>         target.parent.mkdir(parents=True, exist_ok=True)
>         shutil.copy2(path, target)
>         exported += 1
>         print(f"Exported {stage}/{name}")
>
> if not exported:
>     raise SystemExit("No results found; nothing exported")
> print(f"Exported {exported} aggregate files")
> PY
Exported foundation_summary.tsv
Exported new_nested_LFT/family_or_fixed_checkpoint_summary.tsv
Exported new_nested_LFT/family_fixed_cohort_macro_bootstrap.tsv
Exported new_nested_LFT/family_cohort_macro_bootstrap.tsv
Exported new_nested_LFT/foundation_seed_effect_summary.tsv
Exported new_nested_LFT/family_vs_R_effects.tsv
Exported new_nested_LFT/factorial_effects.tsv
Exported new_nested_PFT/family_or_fixed_checkpoint_summary.tsv
Exported new_nested_PFT/family_fixed_cohort_macro_bootstrap.tsv
Exported new_nested_PFT/family_cohort_macro_bootstrap.tsv
Exported new_nested_PFT/foundation_seed_effect_summary.tsv
Exported new_nested_PFT/family_vs_R_effects.tsv
Exported new_nested_PFT/factorial_effects.tsv
Exported 13 aggregate files
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ # Continue only if the export above finished successfully.
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [ "$?" -eq 0 ]; then
>     RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z
>
>     git add -- "$RESULTS" &&
>     git diff --cached --check -- "$RESULTS" &&
>     git diff --cached --stat -- "$RESULTS" &&
>     git --no-pager diff --cached -- "$RESULTS" &&
>     {
>         printf '\nConfirm the displayed tables contain no private identifiers or paths.\n'
>         read -r -p 'Commit and push these results? [y/N] ' answer
>         if [ "$answer" = y ] || [ "$answer" = Y ]; then
>             git commit --only \
>                 -m "Record new foundation training and clinical evaluation results" \
>                 -- "$RESULTS" &&
>             git push origin main
>         fi
>     }
> fi
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:1: trailing whitespace.
+arm    seed    status  cumulative_pooled_anchors       final_validation_context_macro_loss     final_validation_row_macro_loss checkpoint_sha256^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:2: trailing whitespace.
+A_U    17      pass    2764800 0.18014046384228602     0.16128306031227113     4f089fd287a9930bd07d8554b83d129e0c882f69a5ada487dcd7f052acaf4997^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:3: trailing whitespace.
+A_U    24      pass    2764800 0.1565204798874229      0.15248197972774505     627800aad2f55cfecbbec7902b29fa9685e30078d39a5316fddea6672861180c^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:4: trailing whitespace.
+A_U    42      pass    2764800 0.24737875633167503     0.23394186556339264     eaa4bdb740d1949e48f61e35c5a17c95de9ead5ec801e9b1b362cca76f942a3e^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:5: trailing whitespace.
+A_U    64      pass    2764800 0.1409182098477778      0.1486338585615158      d52e6b7c47d00052b2ba23092696ea51dd901432d2459199b1113a5285df6fae^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:6: trailing whitespace.
+A_U    91      pass    2764800 0.2031140409033708      0.1934405165910721      0f7fa63db257371abb5a1b98795b9aac5405e39da3dcdc759bc845c609e297da^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:7: trailing whitespace.
+B_U    17      pass    2764800 0.2195017679954503      0.12582574354057693     697ea0612a154b5ef491b4cb03940e5cab31f6be56c73b1edc884caf630b4c47^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:8: trailing whitespace.
+B_U    24      pass    2764800 0.18339231436264336     0.13251586589015948     fcc5bfc71b1e50f2fad64907319d3cb2e8eed5a7167b4858cdbfabf454991417^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:9: trailing whitespace.
+B_U    42      pass    2764800 0.29906913808649477     0.15267679430791084     63e0059dc1c0e42ea2b43928027ac76b0e97e56cb278e688458d2208101c41d1^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:10: trailing whitespace.
+B_U    64      pass    2764800 0.2329277942288549      0.13069554612894727     a08adcae4d2b7c4289515530cc9e49bb819f70d1460865a375a60d4913e4d609^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:11: trailing whitespace.
+B_U    91      pass    2764800 0.22203883578252911     0.1397110843114822      b86ba32e806f6a4f961d84555cddae665a41f2479a483f2046933dac68d45b16^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:12: trailing whitespace.
+C_U    17      pass    2764800 0.43438177856264804     0.201585198359632       1b0fba1ac077b2f75228ec3d155aca5d2d5cb88593c6571cacb4f48261787c5a^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:13: trailing whitespace.
+C_U    24      pass    2764800 0.4675704357051825      0.22862792647536545     8e1227f5f69d79ef3879f233f1ebaa0d61c0d67c31db9925942e73a8b24e8998^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:14: trailing whitespace.
+C_U    42      pass    2764800 0.3234356010609334      0.15408727526664734     4c18fd982599c8d77c4ed1c62a6658ee4ea5431e00faa011430fd255e59c5f6e^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:15: trailing whitespace.
+C_U    64      pass    2764800 0.413124186185028       0.19871044899248014     b1aa1af8f836de9f8d38bac87f52317476c68b7112f22b21ecd9b7e542ce439b^M
HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv:16: trailing whitespace.
+C_U    91      pass    2764800 0.36105941743734177     0.1986429986425642      f60fdb8f40a0008b8ed8d74f928dfa7a9cee3e531a268031412c49a473a4e4fb^M
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
