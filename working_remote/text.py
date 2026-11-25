https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_REPO=/home/4475918/rx-e07.51U39u
es/raw/HPC_reviewer_experiments/run_20261105
export RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python

cd "$RX_REPO" &&
  "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 \
    --from-stage exposure-finalize --allow-code-change --dry-run(base) 4475918@hpctpa3pl0001:federated-learning-model(ma-model/sources/raw/HPC_reviewer_experiments/run_20261105learning-
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ cd "$RX_REPO" &&
>   "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 \
>     --from-stage exposure-finalize --allow-code-change --dry-run
sbatch --parsable --job-name=rx_E07_exposure-finalize --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/exposure-finalize.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/home/4475918/rx-e07.51U39u,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium /home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/slurm/rx_job.sbatch E07 exposure-finalize
sbatch --parsable --job-name=rx_E07_analyze --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/analyze.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/home/4475918/rx-e07.51U39u,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<exposure-finalize>' /home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/slurm/rx_job.sbatch E07 analyze
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$
