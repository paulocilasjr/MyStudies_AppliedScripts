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





set -a; source hpc/site.env; set +a
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E01
sacct -j 21663681,21663682,21663683 -X --format=JobID%16,JobName%24,State,Elapsed,ExitCode | grep -v COMPLETED
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E02
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E04

less "$RX_ROOT/E01/results/report.md"     # untrained encoder vs A_U/B_U/C_U/R
less "$RX_ROOT/E02/results/report.md"     # variance shares: strategy vs pretraining seed vs cohort
less "$RX_ROOT/E04/results/report.md"     # reproduction check, TOST, required sample size

git pull --ff-only
git log -1 --oneline        # should be your new commit


(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
sacct -j 21663681,21663682,21663683 -X --format=JobID%16,JobName%24,State,Elapsed,ExitCode | grep -v COMPLETED
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E02
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E04(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E01
build                        complete 1/1  failed 0  running 0
rand-plan                    complete 1/1  failed 0  running 0
rand-owners                  complete 48/48  failed 0  running 0
rand-remaining               complete 96/96  failed 0  running 0
rand-finalize                complete 1/1  failed 0  running 0
analyze                      complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ sacct -j 21663681,21663682,21663683 -X --format=JobID%16,JobName%24,State,Elapsed,ExitCode | grep -v COMPLETED
           JobID                  JobName      State    Elapsed ExitCode
---------------- ------------------------ ---------- ---------- --------
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E02
analyze                      complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E04
analyze                      complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ less "$RX_ROOT/E01/results/report.md"     # untrained encoder vs A_U/B_U/C_U/R
.md"     # variance shares: strategy vs pretraining seed vs cohort
less "$RX_ROOT/E04/results/re(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
# E01: Untrained-encoder control (frozen random COMPASS encoder, same heads and LOCO)

Generated 2026-11-06T00:59:36+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

## LFT

Macro responder rate 0.3362; macro expected no-skill trapezoidal AUPRC 0.3685 (random ranking, label-only).

| family | checkpoints | estimate | bc_ci95_low | bc_ci95_high | bootstrap_se |
|---|---|---|---|---|---|
| A_U | 5 | 0.4123 | 0.2830 | 0.5254 | 0.0636 |
| B_U | 5 | 0.4001 | 0.2959 | 0.4892 | 0.0504 |
| C_U | 5 | 0.3996 | 0.2776 | 0.5056 | 0.0584 |
| R | 1 | 0.4574 | 0.3158 | 0.5857 | 0.0691 |
| RAND | 5 | 0.3947 | 0.2760 | 0.4944 | 0.0565 |

Paired contrasts (both resampling scopes; seed-level effects pair each pretrained checkpoint with its own step-zero encoder):

| contrast | scope | estimate | q0025 | q0975 | seed_mean | seed_t_ci95_low | seed_t_ci95_high | exact_sign_flip_p |
|---|---|---|---|---|---|---|---|---|
| pretraining_A_U_minus_RAND | patient_within_fixed_cohorts | 0.0176 | -0.0146 | 0.0555 | 0.0176 | -0.0613 | 0.0964 | 0.5625 |
| pretraining_A_U_minus_RAND | cohort_and_patient | 0.0176 | -0.0392 | 0.0792 | 0.0176 | -0.0613 | 0.0964 | 0.5625 |
| pretraining_B_U_minus_RAND | patient_within_fixed_cohorts | 0.0054 | -0.0270 | 0.0375 | 0.0054 | -0.0296 | 0.0404 | 0.6875 |
| pretraining_B_U_minus_RAND | cohort_and_patient | 0.0054 | -0.0490 | 0.0640 | 0.0054 | -0.0296 | 0.0404 | 0.6875 |
| pretraining_C_U_minus_RAND | patient_within_fixed_cohorts | 0.0049 | -0.0298 | 0.0393 | 0.0049 | -0.0520 | 0.0619 | 0.8750 |
| pretraining_C_U_minus_RAND | cohort_and_patient | 0.0049 | -0.0427 | 0.0545 | 0.0049 | -0.0520 | 0.0619 | 0.8750 |
| RAND_minus_R | patient_within_fixed_cohorts | -0.0627 | -0.1099 | -0.0089 | -0.0627 | -0.1090 | -0.0163 | 0.0625 |
| RAND_minus_R | cohort_and_patient | -0.0627 | -0.1362 | 0.0160 | -0.0627 | -0.1090 | -0.0163 | 0.0625 |

Released R reproduced across the E01 and core packages: max absolute probability difference 0.00e+00 (24/24 fits within 1e-5).

Interpretation guide: a pretrained family is informative beyond architecture and preprocessing only if its paired contrast with RAND is positive with an interval excluding zero. RAND near the no-skill floor shows the heads alone cannot exploit random features; RAND near the trained families shows the protocol, not pretraining, carries the signal.

(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git pull --ff-only
remote: Enumerating objects: 19, done.
remote: Counting objects: 100% (19/19), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 10 (delta 8), reused 10 (delta 8), pack-reused 0 (from 0)
Unpacking objects: 100% (10/10), 2.98 KiB | 25.00 KiB/s, done.
From github.com:paulocilasjr/federated-learning-model
   e11b360..f29529a  main       -> origin/main
Updating e11b360..f29529a
Fast-forward
 HPC_reviewer_experiments/README.md                   |  2 ++
 HPC_reviewer_experiments/rexp/clinical.py            |  9 ++++++---
 HPC_reviewer_experiments/rexp/orchestrate.py         | 49 ++++++++++++++++++++++++++++++++++++++++++-------
 HPC_reviewer_experiments/rx.py                       |  5 ++++-
 HPC_reviewer_experiments/tests/test_orchestration.py | 35 +++++++++++++++++++++++++++++++++++
 5 files changed, 89 insertions(+), 11 deletions(-)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git log -1 --oneline        # should be your new commit
f29529a (HEAD -> main, origin/main, origin/HEAD) experiment fix
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
