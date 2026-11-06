awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next} $h["mode"]=="LFT" && ($h["family"]=="RAND" || $h["family"]=="R"){printf "%-9s %-5s %.3f\n",$h["held_out_cohort"],$h["family"],$h["AUPRC"]}' "$RX_ROOT/E01/results/per_cohort.tsv" | sort

cat "$RX_ROOT/E02/results/report.md" "$RX_ROOT/E04/results/report.md"

set -a; source hpc/site.env; set +a

# Priority: the decisive experiment and the simulator validation
bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh --dry-run
bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh            # also starts the Flower server/client jobs immediately

# Cheap GPU work on existing checkpoints (embeddings, head refits)
bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh
bash HPC_reviewer_experiments/submit/E10_biological_agreement.sh

"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06

tail -20 "$RX_ROOT"/E06/logs/train.*_0.log     # should print one "epoch NNN: train=... val_context_macro=..." line per epoch
for s in E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh
done
