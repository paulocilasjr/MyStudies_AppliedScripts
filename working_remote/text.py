cd /share/lab_goecks/paulo/federated-learning-model
set -a; source hpc/site.env; set +a
git pull --ff-only
git log -1 --oneline

squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol hold
scontrol top 21774381 2>/dev/null || echo "scontrol top not enabled on this cluster; the hold is enough"

squeue -u "$USER" -n compass_fl_srv,compass_fl_cli -o "%.18i %.12j %.3t %R"


squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release

tail -5 /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/launch_fix_20261019T014157Z/federated_project/logs/server.21774380.log


for e in E03 E06 E10 E11; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
