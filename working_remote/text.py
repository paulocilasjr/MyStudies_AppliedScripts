cd /share/lab_goecks/paulo/federated-learning-model

RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z/verification

git add -- "$RESULTS" &&
git diff --cached --check -- "$RESULTS" &&
git --no-pager diff --cached -- "$RESULTS" &&
git commit --only \
  -m "Add sanitized receipts and per-checkpoint clinical metrics" \
  -- "$RESULTS" &&
git push origin main
