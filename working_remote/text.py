https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

"${rx_cmd[@]}" submit E09 && qstat

survival_input="${SURVIVAL_LABELS:-${IATLAS_FEATURES:-}}"

if [[ -n "${CLINICAL_DATASET_ALL16:-}" && -s "$CLINICAL_DATASET_ALL16/manifest.json" ]]; then
  echo "Configured all16 manifest found"
else
  echo "Configured all16 manifest missing"
fi

if [[ -n "$survival_input" && -s "$survival_input" ]]; then
  echo "Configured survival file found"
else
  echo "Configured survival file missing"
fi

if [[ -n "${TEST_PROJECT_ROOT:-}" ]]; then
  arrays="$TEST_PROJECT_ROOT/data/processed/public_ITRP"
  if [[ -d "$arrays" ]]; then
    find "$arrays" -maxdepth 2 -type f -path '*/public_all16*/manifest.json' -print
  fi
  features="${TEST_DOWNLOAD_DIR:-$TEST_PROJECT_ROOT/downloads}/iatlas_ici/iatlas-ici-features.tsv"
  if [[ -s "$features" ]]; then
    printf '%s\n' "$features"
  fi
fi
