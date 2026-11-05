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





(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviwer_experiment/submit/E02_variance_decomposition.sh
bash: HPC_reviwer_experiment/submit/E02_variance_decomposition.sh: No such file or directory
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E02_variance_decomposition.sh
/submit/E04_equivalence_tost.sh/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E02/plan.json
analyze                      job          cpu_large      after=-  REML fits + parametric bootstrap on completed core fits
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E02/submission_20261105T224028+0000.json
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E04_equivalence_tost.sh
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E04/plan.json
analyze                      job          cpu_large      after=-  exact intervals, reproduction check, TOST, power and scaling
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E04/submission_20261105T224029+0000.json
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ scontrol update JobId=21663680 ArrayTaskThrottle=12 MinMemoryNode=32G NumCPUs=4    # rand-owners, pending part
s right nowscontrol: error: Invalid MinMemoryNode value: 32G
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ scontrol update JobId=21663681 ArrayTaskThrottle=12 MinMemoryNode=32G NumCPUs=4    # rand-remaining
scontrol: error: Invalid MinMemoryNode value: 32G
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ sinfo -p red -O NodeList:20,Gres:25,GresUsed:35,CPUsState,FreeMem,StateCompact     # free GPUs right now
NODELIST            GRES                     GRES_USED                          CPUS(A/I/O/T)       FREE_MEM            STATE
hpctpa3pc[0001,0005,gpu:a30:1(S:0)           gpu:a30:1(IDX:0)                   508/452/0/960       132607-486084       mix-
hpctpa3pc0070       gpu:a30:1(S:0)           gpu:a30:0(IDX:N/A)                 0/0/64/64           1011548             drain$
hpctpa3pc0032       gpu:a30:1(S:0)           gpu:a30:0(IDX:N/A)                 0/0/64/64           6035                drain*
hpctpa3pc[0004,0059]gpu:a30:1(S:0)           gpu:a30:0(IDX:N/A)                 0/0/128/128         1013122-1018096     drain
hpctpa3pc0026       gpu:a30:2(S:0-1)         gpu:a30:0(IDX:N/A)                 0/64/0/64           185916              resv
hpctpa3pc[0002-0003,gpu:a30:1(S:0)           gpu:a30:1(IDX:0)                   926/1250/0/2176     62575-717197        mix
hpctpa3pc[0009-0010,gpu:a30:1(S:0)           gpu:a30:1(IDX:0)                   896/0/0/896         92100-501022        alloc
hpctpa3pc0037       gpu:a30:1(S:0)           gpu:a30:0(IDX:N/A)                 64/0/0/64           94197               alloc
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
21663680_[12-47%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Resources)
          21663683  red rx_E01_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21663682  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
 21663681_[0-95%8]  red rx_E01_rand-  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
       21663680_11  red rx_E01_rand-  4475918  R       1:33 1-23:58:27   1   8 gres/gpu:  64G hpctpa3pc0006
       21663680_10  red rx_E01_rand-  4475918  R       3:03 1-23:56:57   1   8 gres/gpu:  64G hpctpa3pc0066
        21663680_9  red rx_E01_rand-  4475918  R       3:26 1-23:56:34   1   8 gres/gpu:  64G hpctpa3pc0013
        21663680_8  red rx_E01_rand-  4475918  R       3:48 1-23:56:12   1   8 gres/gpu:  64G hpctpa3pc0002
        21663680_7  red rx_E01_rand-  4475918  R       4:30 1-23:55:30   1   8 gres/gpu:  64G hpctpa3pc0056
        21663680_6  red rx_E01_rand-  4475918  R       6:49 1-23:53:11   1   8 gres/gpu:  64G hpctpa3pc0054
          21668090  red rx_E02_analy  4475918  R       0:44 1-23:59:16   1  16       N/A 128G hpctpa3pc0014
          21668091  red rx_E04_analy  4475918  R       0:44 1-23:59:16   1  16       N/A 128G hpctpa3pc0014
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E01
,ExitCode,NodeListbuild                        complete 1/1  failed 0  running 0
rand-plan                    complete 1/1  failed 0  running 0
rand-owners                  complete 6/48  failed 0  running 6
rand-remaining               complete 0/96  failed 0  running 0
rand-finalize                complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ sacct -j 21663680 -X --format=JobID%16,State,Elapsed,ExitCode,NodeList
           JobID      State    Elapsed ExitCode        NodeList
---------------- ---------- ---------- -------- ---------------
      21663680_0  COMPLETED   00:17:16      0:0   hpctpa3pc0066
      21663680_1  COMPLETED   00:14:12      0:0   hpctpa3pc0066
      21663680_2  COMPLETED   00:12:24      0:0   hpctpa3pc0013
      21663680_3  COMPLETED   00:12:02      0:0   hpctpa3pc0002
      21663680_4  COMPLETED   00:14:14      0:0   hpctpa3pc0006
      21663680_5  COMPLETED   00:05:42      0:0   hpctpa3pc0054
      21663680_6    RUNNING   00:07:17      0:0   hpctpa3pc0054
      21663680_7    RUNNING   00:04:58      0:0   hpctpa3pc0056
      21663680_8    RUNNING   00:04:16      0:0   hpctpa3pc0002
      21663680_9    RUNNING   00:03:54      0:0   hpctpa3pc0013
     21663680_10    RUNNING   00:03:31      0:0   hpctpa3pc0066
     21663680_11    RUNNING   00:02:01      0:0   hpctpa3pc0006
21663680_[12-47+    PENDING   00:00:00      0:0   None assigned
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
