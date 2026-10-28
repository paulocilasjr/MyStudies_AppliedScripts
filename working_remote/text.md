RUN_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/memory_fix_20261019T143329Z

for stage in sample_objective new_pilot new_nested_LFT new_nested_PFT; do
  result_dir="$RUN_ROOT/${stage}_launch/finalized"
  if [ -d "$result_dir" ]; then
    echo "=== $stage ==="
    find "$result_dir" -maxdepth 1 -type f -printf '%f\n' | sort
  else
    echo "=== $stage: finalized directory not found ==="
  fi
done
