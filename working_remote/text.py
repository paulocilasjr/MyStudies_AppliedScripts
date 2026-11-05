set -a; source hpc/site.env; set +a
for v in RX_PYTHON_TEST RX_PYTHON_FED RX_RESOURCES COMPASS_SOURCE FOUNDATION_DATASET CLINICAL_DATASET NEW_MODELS \
         CORE_LFT_PACKAGE CORE_PFT_PACKAGE PUBLISHED_REFERENCE CLINICAL_COST_REFERENCE; do
  [[ -e "${!v}" ]] && echo "ok       $v" || echo "MISSING  $v=${!v}"
done
ls "$CORE_ITERATION_ROOT/sample_objective/C_U_seed17.task.json"     # needed by E11
git check-ignore -q --no-index "$RX_ROOT" && echo "RX_ROOT is git-ignored"

srun --cpus-per-task=4 --mem=16G --time=00:45:00 ${CLINICAL_PARTITION:+--partition=$CLINICAL_PARTITION} \
  "$RX_PYTHON_TEST" -m unittest discover -s HPC_reviewer_experiments/tests -v


bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh --dry-run   # writes the plan, prints graph + sbatch
bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh             # one CPU job, no training


bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh --dry-run
bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh


for s in E02_variance_decomposition E03_seed_ensembling E04_equivalence_tost E10_biological_agreement E11_hpc_deployment; do
  bash HPC_reviewer_experiments/submit/$s.sh
done

for s in E06_federated_compass_recipe E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh --dry-run && bash HPC_reviewer_experiments/submit/$s.sh
done

conda activate compass-foundation-test
export TEST_CODE_DIR="$PWD/compass_hpc_foundation_model_test"
export TEST_PROJECT_ROOT=/share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test
export SYNAPSE_AUTH_TOKEN_FILE="$HOME/.config/synapse/compass_pat"
export COMPASS_RSCRIPT="$(conda run -n compass-data which Rscript)"
export PUBLIC_COHORT_SET=all16
export PUBLIC_RUN_TAG=public_all16_$(date -u +%Y%m%d_%H%M%SZ)
source "$TEST_CODE_DIR/config/settings.env"
bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
echo "$PUBLIC_ITRP_PROCESSED_DIR"          # this becomes CLINICAL_DATASET_ALL16
conda deactivate


bash HPC_reviewer_experiments/submit/E13_broader_validation.sh --dry-run && bash HPC_reviewer_experiments/submit/E13_broader_validation.sh


bash HPC_reviewer_experiments/submit/E09_checkpoint_proxies.sh



set -a; source hpc/site.env; set +a
squeue -u "$USER"
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06          # per-stage complete/failed/running
ls "$RX_ROOT/E06/logs/"                                              # one log per job / array element

# After fixing a failure, resubmit from the failed stage (finished work is reused)
bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh --from-stage recipe-owners

# Wrong path seen in a dry run, before any submit: fix hpc/site.env, then re-plan
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E06 --force-new

# Export aggregate results into the repo (rechecked for patient-level content), review, then commit
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py export E06





(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh --dry-run
ments/submit/E01_untrained_encoder.sh/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/plan.json
build                        job          cpu            after=-  construct 5 untrained encoders + verify step-zero tensors
rand-plan                    job          cpu            after=build  freeze + preflight clinical panel rand
rand-owners                  array[48]    clinical_gpu   after=rand-plan  inner selection owners (fine-tuning seed 24)
rand-remaining               array[96]    clinical_gpu   after=rand-owners  remaining fine-tuning seeds (cached selection)
rand-finalize                job          cpu_large      after=rand-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=rand-finalize  RAND vs A_U/B_U/C_U/R with paired bootstrap
sbatch --parsable --job-name=rx_E01_build --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/build.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E01 build
sbatch --parsable --job-name=rx_E01_rand-plan --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/rand-plan.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<build>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E01 rand-plan
sbatch --parsable --job-name=rx_E01_rand-owners --cpus-per-task=8 --mem=64G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/rand-owners.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-47%8 '--dependency=afterok:<rand-plan>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E01 rand-owners
sbatch --parsable --job-name=rx_E01_rand-remaining --cpus-per-task=8 --mem=64G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/rand-remaining.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-95%8 '--dependency=afterok:<rand-owners>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E01 rand-remaining
sbatch --parsable --job-name=rx_E01_rand-finalize --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/rand-finalize.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<rand-remaining>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E01 rand-finalize
sbatch --parsable --job-name=rx_E01_analyze --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/logs/analyze.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<rand-finalize>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E01 analyze
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh
build                        job          cpu            after=-  construct 5 untrained encoders + verify step-zero tensors
rand-plan                    job          cpu            after=build  freeze + preflight clinical panel rand
rand-owners                  array[48]    clinical_gpu   after=rand-plan  inner selection owners (fine-tuning seed 24)
rand-remaining               array[96]    clinical_gpu   after=rand-owners  remaining fine-tuning seeds (cached selection)
rand-finalize                job          cpu_large      after=rand-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=rand-finalize  RAND vs A_U/B_U/C_U/R with paired bootstrap
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E01/submission_20261105T220311+0000.json
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E01
build                        complete 1/1  failed 0  running 0
rand-plan                    complete 0/1  failed 0  running 1
rand-owners                  complete 0/48  failed 0  running 0
rand-remaining               complete 0/96  failed 0  running 0
rand-finalize                complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21663683  red rx_E01_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21663682  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
 21663681_[0-95%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
 21663680_[0-47%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21663679  red rx_E01_rand-  4475918  R       0:17    7:59:43   1   4       N/A  32G hpctpa3pc0003
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
