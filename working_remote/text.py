https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

rx_rscript=$(conda run -n compass-data which Rscript) &&
  export COMPASS_RSCRIPT="$rx_rscript" &&
  "$COMPASS_RSCRIPT" --version

export PUBLIC_DOWNLOAD_FASTQ=0 PUBLIC_MIN_COHORTS=16 PUBLIC_COHORTS=""
unset PUBLIC_RUN_TABLE PUBLIC_COMPASS_DIR PUBLIC_ITRP_RAW_DIR PUBLIC_ITRP_PROCESSED_DIR
source "$TEST_CODE_DIR/config/settings.env"
export CLINICAL_DATASET_ALL16="$PUBLIC_ITRP_PROCESSED_DIR"

if [[ -z "${SYNAPSE_AUTH_TOKEN_FILE:-}" && -s "$HOME/.config/synapse/compass_pat" ]]; then
  export SYNAPSE_AUTH_TOKEN_FILE="$HOME/.config/synapse/compass_pat"
fi

TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
  bash "$TEST_CODE_DIR/scripts/submit_public_pipeline.sh"
