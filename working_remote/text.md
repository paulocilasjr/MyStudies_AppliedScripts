find \
  /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/memory_fix_20261019T143329Z \
  /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/launch_fix_20261019T014157Z/federated_project/runs \
  -type f \( \
    -name 'foundation_summary.json' -o \
    -name 'completion_receipt.json' -o \
    -name 'report.md' -o \
    -name 'macro_summary.tsv' -o \
    -name 'family_or_fixed_checkpoint_summary.tsv' -o \
    -name 'models.tsv' \
  \) -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort -r
