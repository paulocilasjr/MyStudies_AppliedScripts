(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv")
path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
print("Fixed foundation_summary.tsv line endings")
PY

RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z

git add -- "$RESULTS" &&
git diff --cached --check -- "$RESULTS" &&
git diff --cached --stat -- "$RESULTS" &&
git commit --only \
  -m "Record new foundation training and clinical evaluation results" \
  -- "$RESULTS" &&
git push origin main(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ python3 - <<'PY'
> from pathlib import Path
> path = Path("HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv")
> path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
> print("Fixed foundation_summary.tsv line endings")
> PY
Fixed foundation_summary.tsv line endings
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ git add -- "$RESULTS" &&
> git diff --cached --check -- "$RESULTS" &&
> git diff --cached --stat -- "$RESULTS" &&
> git commit --only \
>   -m "Record new foundation training and clinical evaluation results" \
>   -- "$RESULTS" &&
> git push origin main
 HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv                                 | 16 ++++++++++++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/factorial_effects.tsv                   | 46 ++++++++++++++++++++++++++++++++++++++++++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_cohort_macro_bootstrap.tsv       |  7 +++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_fixed_cohort_macro_bootstrap.tsv |  7 +++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_or_fixed_checkpoint_summary.tsv  |  5 +++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_vs_R_effects.tsv                 | 46 ++++++++++++++++++++++++++++++++++++++++++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/foundation_seed_effect_summary.tsv      |  7 +++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/factorial_effects.tsv                   | 46 ++++++++++++++++++++++++++++++++++++++++++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_cohort_macro_bootstrap.tsv       |  7 +++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_fixed_cohort_macro_bootstrap.tsv |  7 +++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_or_fixed_checkpoint_summary.tsv  |  5 +++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_vs_R_effects.tsv                 | 46 ++++++++++++++++++++++++++++++++++++++++++++++
 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/foundation_seed_effect_summary.tsv      |  7 +++++++
 13 files changed, 252 insertions(+)
[main c0c5965] Record new foundation training and clinical evaluation results
 13 files changed, 252 insertions(+)
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/factorial_effects.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_cohort_macro_bootstrap.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_fixed_cohort_macro_bootstrap.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_or_fixed_checkpoint_summary.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/family_vs_R_effects.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_LFT/foundation_seed_effect_summary.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/factorial_effects.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_cohort_macro_bootstrap.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_fixed_cohort_macro_bootstrap.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_or_fixed_checkpoint_summary.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/family_vs_R_effects.tsv
 create mode 100644 HPC_analysis_new/results/memory_fix_20261019T143329Z/new_nested_PFT/foundation_seed_effect_summary.tsv
Enumerating objects: 23, done.
Counting objects: 100% (23/23), done.
Delta compression using up to 64 threads
Compressing objects: 100% (20/20), done.
Writing objects: 100% (20/20), 18.74 KiB | 3.75 MiB/s, done.
Total 20 (delta 10), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (10/10), completed with 3 local objects.
To github.com:paulocilasjr/federated-learning-model.git
   2f862f0..c0c5965  main -> main
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
