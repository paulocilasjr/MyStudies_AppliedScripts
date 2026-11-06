cd /share/lab_goecks/paulo/federated-learning-model
set -a; source hpc/site.env; set +a

for e in E01 E02 E03 E04 E05 E06 E07 E08 E08B E10 E11 E12; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done

squeue -u "$USER" -o "%.18i %.24j %.9T %.11M %.4D %R"


ls -t "$RX_ROOT"/E0{6,7,8}*/logs/train.*.log "$RX_ROOT"/E12/logs/train.*.log 2>/dev/null | head -8 | while read f; do echo "== $f"; tail -n 2 "$f"; done

ls -t "$RX_ROOT"/E11/logs/*.log | head -4 | while read f; do echo "== $f"; tail -n 3 "$f"; done


sacct -X -u "$USER" -S now-2days -s F,TO,OOM,NF -o JobID%20,JobName%24,State,Elapsed,ExitCode


cat "$RX_ROOT/E06/results/report.md"

squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release

