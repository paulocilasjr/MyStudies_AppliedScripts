cd /share/lab_goecks/paulo/federated-learning-model

python3 - <<'PY'
from pathlib import Path
path = Path("HPC_analysis_new/results/memory_fix_20261019T143329Z/foundation_summary.tsv")
path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
print("Fixed foundation_summary.tsv line endings")
PY

RESULTS=HPC_analysis_new/results/memory_fix_20261019T143329Z

git add -- "$RESULTS" &&
git diff --cached --check -- "$RESULTS" &&
git diff --cached --stat -- "$RESULTS" &&
git commit --only \
  -m "Record new foundation training and clinical evaluation results" \
  -- "$RESULTS" &&
git push origin main
