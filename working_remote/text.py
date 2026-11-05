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





(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ column -t -s $'\t' "$RX_ROOT/E01/results/random_encoder_build.tsv"   # matches_A_U_step_zero should be True for all 5
open('$RX_ROOT/E01/clinical/rand/package/rx_preflight.json')); print(r['status'], r['cost_gate'].get('estimated_gpu_hours'), [g['gate'] for g in r['stock_preflight']['unresolved_gates']])"seed  step_zero_receipt_checked  matches_A_U_step_zero
17    True                       True
24    True                       True
42    True                       True
64    True                       True
91    True                       True
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ # once rand-plan finishes:
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "$RX_PYTHON_TEST" -c "import json; r=json.load(open('$RX_ROOT/E01/clinical/rand/package/rx_preflight.json')); print(r['status'], r['cost_gate'].get('estimated_gpu_hours'), [g['gate'] for g in r['stock_preflight']['unresolved_gates']])"
pass 10.379510421646021 ['repeated_person_linkage', 'measured_pilot_cost']
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21663680_[1-47%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Resources)
          21663683  red rx_E01_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21663682  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
 21663681_[0-95%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
        21663680_0  red rx_E01_rand-  4475918  R       3:13 1-23:56:47   1   8 gres/gpu:  64G hpctpa3pc0066
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
