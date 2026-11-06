cd /share/lab_goecks/paulo/federated-learning-model
set -a; source hpc/site.env; set +a
git pull --ff-only
git log -1 --oneline                  # expect: e73c6d5 bug fix E11

squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o "%A %j" | sort -u

If this prints anything, you already restarted training, so skip to step 3. If it prints nothing, restart it:


squeue -u "$USER" -h -o "%A %j" | awk '$2 ~ /^rx_E(06|07|08|08B|12)_/ {print $1}' | sort -u | xargs -r scancel
for s in E06_federated_compass_recipe E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh --from-stage train --allow-code-change
done

  "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E11 --force-new
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh
grep '"code_inputs_rebound"' "$RX_ROOT/E11/deploy/deployments.json"          # should be a number > 0
squeue -u "$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val   # the Flower server/client/validation jobs

  "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E03
grep -l Traceback "$RX_ROOT"/E03/logs/*.log | xargs -r tail -n 4

  squeue -u "$USER" -h -o "%A %j" | awk '$2 ~ /^rx_E03_/ {print $1}' | sort -u | xargs -r scancel
bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh --only predictions embeddings --allow-code-change

  for e in E03 E06 E07 E08 E08B E10 E11 E12; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done

tail -3 "$(ls -t "$RX_ROOT"/E06/logs/train.*_0.log | head -1)"
