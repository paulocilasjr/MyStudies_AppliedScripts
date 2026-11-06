awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next} $h["pair_type"] !~ /^\[/ {printf "%-13s %-10s %-24s %.3f\n",$h["subset"],$h["view"],$h["pair_type"],$h["mean_linear_cka"]}' "$RX_ROOT/E10/results/cka_summary.tsv"
column -t -s $'\t' "$RX_ROOT/E10/results/attribution_by_model.tsv"


squeue -u "$USER" -h -o "%A %j %T %r" | sort -u

squeue -u "$USER" -h -t PD -o "%A %r" | awk '$2=="DependencyNeverSatisfied"{print $1}' | sort -u | xargs -r scancel

EXP=E07     # E03, E06, E07, E08, E08B, E10, E12 ...
squeue -u "$USER" -h -o "%A %j" | awk -v p="^rx_${EXP}_" '$2 ~ p {print $1}' | sort -u | xargs -r scancel

bash HPC_reviewer_experiments/submit/E07_tumor_exposure.sh --from-stage <failed-stage> --allow-code-change
