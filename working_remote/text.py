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





(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ sacct -j 21663680 -X --format=JobID%16,State,Elapsed,ExitCode,NodeList
           JobID      State    Elapsed ExitCode        NodeList
---------------- ---------- ---------- -------- ---------------
      21663680_0  COMPLETED   00:17:16      0:0   hpctpa3pc0066
      21663680_1  COMPLETED   00:14:12      0:0   hpctpa3pc0066
      21663680_2  COMPLETED   00:12:24      0:0   hpctpa3pc0013
      21663680_3  COMPLETED   00:12:02      0:0   hpctpa3pc0002
      21663680_4  COMPLETED   00:14:14      0:0   hpctpa3pc0006
      21663680_5  COMPLETED   00:05:42      0:0   hpctpa3pc0054
      21663680_6  COMPLETED   00:16:00      0:0   hpctpa3pc0054
      21663680_7  COMPLETED   00:16:56      0:0   hpctpa3pc0056
      21663680_8  COMPLETED   00:10:56      0:0   hpctpa3pc0002
      21663680_9  COMPLETED   00:06:15      0:0   hpctpa3pc0013
     21663680_10  COMPLETED   00:13:15      0:0   hpctpa3pc0066
     21663680_11  COMPLETED   00:14:39      0:0   hpctpa3pc0006
     21663680_12  COMPLETED   00:09:13      0:0   hpctpa3pc0013
     21663680_13  COMPLETED   00:08:21      0:0   hpctpa3pc0002
     21663680_14  COMPLETED   00:11:49      0:0   hpctpa3pc0054
     21663680_15  COMPLETED   00:11:14      0:0   hpctpa3pc0066
     21663680_16  COMPLETED   00:11:23      0:0   hpctpa3pc0068
     21663680_17  COMPLETED   00:07:14      0:0   hpctpa3pc0013
     21663680_18  COMPLETED   00:13:26      0:0   hpctpa3pc0056
     21663680_19  COMPLETED   00:08:36      0:0   hpctpa3pc0006
     21663680_20  COMPLETED   00:08:31      0:0   hpctpa3pc0002
     21663680_21  COMPLETED   00:05:02      0:0   hpctpa3pc0013
     21663680_22  COMPLETED   00:12:30      0:0   hpctpa3pc0054
     21663680_23  COMPLETED   00:13:46      0:0   hpctpa3pc0066
     21663680_24  COMPLETED   00:08:18      0:0   hpctpa3pc0006
     21663680_25  COMPLETED   00:06:05      0:0   hpctpa3pc0066
     21663680_26  COMPLETED   00:09:08      0:0   hpctpa3pc0066
     21663680_27  COMPLETED   00:09:44      0:0   hpctpa3pc0058
     21663680_28  COMPLETED   00:07:20      0:0   hpctpa3pc0017
     21663680_29  COMPLETED   00:06:48      0:0   hpctpa3pc0069
     21663680_30  COMPLETED   00:10:04      0:0   hpctpa3pc0066
     21663680_31  COMPLETED   00:10:56      0:0   hpctpa3pc0068
     21663680_32  COMPLETED   00:13:21      0:0   hpctpa3pc0013
     21663680_33  COMPLETED   00:11:17      0:0   hpctpa3pc0058
     21663680_34  COMPLETED   00:09:57      0:0   hpctpa3pc0069
     21663680_35  COMPLETED   00:09:00      0:0   hpctpa3pc0017
     21663680_36  COMPLETED   00:12:25      0:0   hpctpa3pc0002
     21663680_37  COMPLETED   00:07:41      0:0   hpctpa3pc0006
     21663680_38  COMPLETED   00:10:52      0:0   hpctpa3pc0066
     21663680_39  COMPLETED   00:14:18      0:0   hpctpa3pc0068
     21663680_40  COMPLETED   00:17:41      0:0   hpctpa3pc0058
     21663680_41  COMPLETED   00:14:06      0:0   hpctpa3pc0017
     21663680_42  COMPLETED   00:15:10      0:0   hpctpa3pc0013
     21663680_43  COMPLETED   00:11:35      0:0   hpctpa3pc0069
     21663680_44  COMPLETED   00:14:26      0:0   hpctpa3pc0006
     21663680_45  COMPLETED   00:09:07      0:0   hpctpa3pc0002
     21663680_46  COMPLETED   00:17:38      0:0   hpctpa3pc0066
     21663680_47  COMPLETED   00:18:38      0:0   hpctpa3pc0068
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
