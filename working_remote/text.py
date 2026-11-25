tail -n 40 "$TEST_LOG_DIR/$PUBLIC_RUN_TAG/controller.22458294.log"

if [[ -s "$CLINICAL_DATASET_ALL16/manifest.json" ]]; then
  "${rx_cmd[@]}" plan E13 && "${rx_cmd[@]}" submit E13 --dry-run
else
  echo "Waiting for the 16-cohort manifest."
fi

"${rx_cmd[@]}" submit E13 && qstat
