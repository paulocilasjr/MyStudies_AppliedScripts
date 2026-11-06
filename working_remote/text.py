set -a; source hpc/site.env; set +a
tail -n 2 "$(ls -t "$RX_ROOT"/E03/logs/embeddings.*.log | head -1)"
# expect: ValueError: Object arrays cannot be loaded when allow_pickle=False

git pull --ff-only
git log -1 --oneline


bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh --only embeddings --allow-code-change

squeue -u "$USER" -n compass_fl_srv,compass_fl_cli -o "%.18i %.12j %.3t %R"

for e in E03 E10; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
cat "$RX_ROOT/E03/results/report.md"
cat "$RX_ROOT/E10/results/report.md"      # once its analyze is complete
