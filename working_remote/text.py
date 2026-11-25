https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

cd /share/lab_goecks/paulo/federated-learning-model
export REPO="$PWD"
set -a
source "${RX_SITE_ENV:-$REPO/hpc/site.env}"
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
  printf '%s\n' "E13 needs the prepared 16-cohort dataset and a survival input file."
fi
