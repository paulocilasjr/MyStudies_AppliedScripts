https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

export IATLAS_FEATURES="$PWD/compass_foundation_model_test/downloads/iatlas_ici/iatlas-ici-features.tsv"
unset SURVIVAL_LABELS
export TEST_CODE_DIR="$PWD/compass_hpc_foundation_model_test"
export PUBLIC_RUN_TAG="public_all16_e13_$(date -u +%Y%m%d_%H%M%SZ)"
export CLINICAL_DATASET_ALL16="$TEST_PROJECT_ROOT/data/processed/public_ITRP/$PUBLIC_RUN_TAG"

PUBLIC_COHORT_SET=all16 TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
  bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"

test -s "$CLINICAL_DATASET_ALL16/manifest.json" &&
  "${rx_cmd[@]}" plan E13 &&
  "${rx_cmd[@]}" submit E13 --dry-run
