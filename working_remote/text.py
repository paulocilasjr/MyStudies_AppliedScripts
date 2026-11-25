https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
ENV:-$REPO/hpc/site.env}"
set +a
export RX_ROOT="$PWD/sources/raw/HPC_reviewer_experiments/run_20261105"
unset RX_REPO RX_PYTHON
rx_cmd=("$RX_PYTHON_TEST" "$PWD/HPC_reviewer_experiments/rx.py")

"${rx_cmd[@]}" plan E09 && "${rx_cmd[@]}" submit E09 --dry-run

survival_input="${SURVIVAL_LABELS:-${IATLAS_FEATURES:-}}"
if [[ -n "${CLINICAL_DATASET_ALL16:-}" &&
      -s "$CLINICAL_DATASET_ALL16/manifest.json" &&
      -s "$survival_input" ]]; then
  "${rx_cmd[@]}" plan E13 && "${rx_cmd[@]}" submit E13 --dry-run
else
  printf '%s\n' "E13 needs the prepared 16-cohort dataset and a survival in(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export REPO="$PWD"
put file."
fi(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ set -a
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ source "${RX_SITE_ENV:-$REPO/hpc/site.env}"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ set +a
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_ROOT="$PWD/sources/raw/HPC_reviewer_experiments/run_20261105"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ unset RX_REPO RX_PYTHON
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ rx_cmd=("$RX_PYTHON_TEST" "$PWD/HPC_reviewer_experiments/rx.py")
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "${rx_cmd[@]}" plan E09 && "${rx_cmd[@]}" submit E09 --dry-run

/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E09/plan.json
sbatch --parsable --job-name=rx_E09_probe-embed --cpus-per-task=8 --mem=64G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E09/logs/probe-embed.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-137%8 /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E09 probe-embed
sbatch --parsable --job-name=rx_E09_analyze --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E09/logs/analyze.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<probe-embed>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E09 analyze
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ survival_input="${SURVIVAL_LABELS:-${IATLAS_FEATURES:-}}"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -n "${CLINICAL_DATASET_ALL16:-}" &&
>       -s "$CLINICAL_DATASET_ALL16/manifest.json" &&
>       -s "$survival_input" ]]; then
>   "${rx_cmd[@]}" plan E13 && "${rx_cmd[@]}" submit E13 --dry-run
> else
>   printf '%s\n' "E13 needs the prepared 16-cohort dataset and a survival input file."
> fi
E13 needs the prepared 16-cohort dataset and a survival input file.
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
