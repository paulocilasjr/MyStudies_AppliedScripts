https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

sacct -X -j 22457666,22457467 -o JobID,JobName%36,State%24,ExitCode,Elapsed
log="$TEST_LOG_DIR/$PUBLIC_RUN_TAG/controller.22457666.log"
if [[ -f "$log" ]]; then
  tail -n 40 "$log"
fi

conda create -n compass-e13-r --override-channels -c conda-forge 'r-base>=4.3' &&
  rx_rscript=$(conda run -n compass-e13-r which Rscript) &&
  export COMPASS_RSCRIPT="$rx_rscript"

"$COMPASS_RSCRIPT" --vanilla -e 'cat(R.version.string, "\n")' &&
  TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
  bash "$TEST_CODE_DIR/scripts/submit_public_pipeline.sh"
