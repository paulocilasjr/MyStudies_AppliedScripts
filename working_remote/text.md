find . -type f \( \
  -name 'foundation_summary.json' -o \
  -name 'completion_receipt.json' -o \
  -name 'aggregation_manifest.json' -o \
  -name 'validation_report.json' -o \
  -name 'run_manifest.json' -o \
  -name 'model_macro_auprc_intervals.tsv' -o \
  -name 'macro_summary.tsv' \
\) -printf '%TY-%Tm-%Td %TH:%TM %p\n' \
  | sort -r | head -80