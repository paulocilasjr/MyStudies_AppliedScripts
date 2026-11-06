awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next} $h["contrast"]=="federation_C_U_minus_B_U"{printf "%s %-28s %-26s %.3f [%.4f, %.4f] %s\n",$h["mode"],$h["scope"],$h["margin_id"],$h["margin"],$h["ci90_low"],$h["ci90_high"],$h["conclusion"]}' "$RX_ROOT/E04/results/tost.tsv"

git pull --ff-only
set -a; source hpc/site.env; set +a
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E11 --force-new     # E11 never submitted, so re-planning is allowed
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh
grep -E '"code_inputs_rebound"|"run_dir"' "$RX_ROOT/E11/deploy/deployments.json"
squeue -u "$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val     # the Flower pipeline jobs


tail -5 "$RX_ROOT"/E06/logs/train.*_0.log      # expect "CR_CEN seed 17 epoch 001: train=... val_context_macro=..."
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06

squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scancel

squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol hold
# later:
squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release
