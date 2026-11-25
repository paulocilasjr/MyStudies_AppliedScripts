https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ rx_runs=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments
uns"/*; do
  [[ -d "$run" ]] || continue
  printf '\n%s\n' "${run##*/}"
  for exp in E{01..08} E08B E{09..13}; do
    dir="$run/$exp"
    if [[ -s "$dir/results/report.md" && -s "$dir/results/results_receipt.json" ]]; then
      status="report and receipt present"
    elif [[ -s "$dir/plan.json" ]]; then
      status="plan present, result bundle incomplete"
    else
      status="no plan in this run"
    fi
    printf '%-5s %s\n' "$exp" "$status"
  done
done(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ for run in "$rx_runs"/*; do
>   [[ -d "$run" ]] || continue
>   printf '\n%s\n' "${run##*/}"
>   for exp in E{01..08} E08B E{09..13}; do
>     dir="$run/$exp"
>     if [[ -s "$dir/results/report.md" && -s "$dir/results/results_receipt.json" ]]; then
>       status="report and receipt present"
>     elif [[ -s "$dir/plan.json" ]]; then
>       status="plan present, result bundle incomplete"
>     else
>       status="no plan in this run"
>     fi
>     printf '%-5s %s\n' "$exp" "$status"
>   done
> done

run_20261105
E01   report and receipt present
E02   report and receipt present
E03   report and receipt present
E04   report and receipt present
E05   report and receipt present
E06   report and receipt present
E07   report and receipt present
E08   report and receipt present
E08B  report and receipt present
E09   no plan in this run
E10   report and receipt present
E11   report and receipt present
E12   report and receipt present
E13   no plan in this run
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
