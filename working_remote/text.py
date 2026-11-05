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




(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ srun --cpus-per-task=4 --mem=16G --time=00:45:00 ${CLINICAL_PARTITION:+--partition=$CLINICAL_PARTITION} \
>   "$RX_PYTHON_TEST" -m unittest discover -s HPC_reviewer_experiments/tests -v

Validated bootstrap study 1/4
Validated bootstrap study 2/4
Validated bootstrap study 3/4
Validated bootstrap study 4/4
test_contrasts_and_family_intervals_match_stock_finalizer (test_bootstrap_reproduction.BootstrapReproductionTest) ... ok
test_seed_level_effects_pair_matching_seeds (test_bootstrap_reproduction.BootstrapReproductionTest) ... ok
central seed 17 epoch 001: train=0.979223 val_context_macro=0.972261
central seed 17 epoch 002: train=0.983078 val_context_macro=0.985225
quota seed 17 epoch 001: train=1.027265 val_context_macro=0.975247
quota seed 17 epoch 002: train=0.970865 val_context_macro=0.974476
test_centralized_and_source_quotas (test_engine.EngineTest) ... ok
dp seed 17 round 001: train=1.052888 val_context_macro=0.983959
dp seed 17 round 002: train=0.946981 val_context_macro=0.982713
test_dp_run_meets_target_epsilon_with_holdout_and_snapshot (test_engine.EngineTest) ... ok
test_dp_vmap_and_loop_gradients_agree (test_engine.EngineTest) ... ok
fed_fedavg seed 17 round 001: train=0.955597 val_context_macro=0.990691
fed_fedavg seed 17 round 002: train=1.042367 val_context_macro=0.991874
fed_fedprox seed 17 round 001: train=0.955597 val_context_macro=0.990691
fed_fedprox seed 17 round 002: train=1.042367 val_context_macro=0.991874
fed_scaffold seed 17 round 001: train=0.955597 val_context_macro=0.990691
fed_scaffold seed 17 round 002: train=1.042367 val_context_macro=0.991711
fed_fedadam seed 17 round 001: train=0.955597 val_context_macro=0.988276
fed_fedadam seed 17 round 002: train=1.046396 val_context_macro=0.990494
test_federated_algorithms_run_and_report_telemetry (test_engine.EngineTest) ... ok
test_flower_compat_matches_flower_client_recipe (test_engine.EngineTest)
compat seed 17 round 001: train=1.042707 val_context_macro=0.985828
Replays 03_flower_client.py's round-1 fit for the TCGA client and compares exact tensors. ... ok
resume_ref_central seed 17 epoch 001: train=0.979223 val_context_macro=0.972261
resume_ref_central seed 17 epoch 002: train=0.983078 val_context_macro=0.985225
resume_central seed 17 epoch 001: train=0.979223 val_context_macro=0.972261
resume_central seed 17 epoch 002: train=0.983078 val_context_macro=0.985225
resume_ref_federated seed 17 round 001: train=0.955597 val_context_macro=0.990691
resume_ref_federated seed 17 round 002: train=1.042367 val_context_macro=0.991874
resume_federated seed 17 round 001: train=0.955597 val_context_macro=0.990691
resume_federated seed 17 round 002: train=1.042367 val_context_macro=0.991874
test_resume_reproduces_uninterrupted_run (test_engine.EngineTest) ... ok
tss seed 17 round 001: train=0.995010 val_context_macro=0.981261
tss seed 17 round 002: train=1.030073 val_context_macro=0.979781
test_tissue_source_site_partition (test_engine.EngineTest) ... ok
test_array_sizes_follow_the_declared_panels (test_orchestration.OrchestrationTest) ... ok
test_every_experiment_plans_and_dry_runs (test_orchestration.OrchestrationTest) ... ok
test_plan_is_frozen (test_orchestration.OrchestrationTest) ... ok
test_schemes_keep_people_and_sites_whole (test_statistics.PartitionTest) ... ok
test_full_batch_closed_form_and_monotonicity (test_statistics.PrivacyAccountingTest) ... ok
test_series_matches_numerical_integration (test_statistics.PrivacyAccountingTest) ... ok
test_recovers_crossed_components (test_statistics.RemlTest) ... ok
test_woodbury_criterion_equals_dense_reml (test_statistics.RemlTest) ... ok
test_cka_invariances (test_statistics.StatisticsTest) ... ok
test_cox_and_concordance (test_statistics.StatisticsTest) ... ok
test_expected_random_auprc_matches_sklearn_simulation (test_statistics.StatisticsTest) ... ok
test_rank_correlations_match_scipy (test_statistics.StatisticsTest) ... ok
test_tost_and_sample_size (test_statistics.StatisticsTest) ... ok
test_trapezoidal_auprc_matches_project_metric (test_statistics.StatisticsTest) ... ok
test_weighted_auroc_matches_sklearn_on_expanded_rows (test_statistics.StatisticsTest) ... ok

----------------------------------------------------------------------
Ran 24 tests in 8.723s

OK
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh --dry-run   # writes the plan, prints graph + sbatch
 CPU job, no training/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/plan.json
analyze                      job          cpu_large      after=-  per-cohort AUPRC/AUROC, lifts, concentration

sbatch --parsable --job-name=rx_E05_analyze --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/logs/analyze.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E05 analyze
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh             # one CPU job, no training
analyze                      job          cpu_large      after=-  per-cohort AUPRC/AUROC, lifts, concentration
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/submission_20261105T214902+0000.json
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21661973  red rx_E05_analy  4475918  R       0:04 1-23:59:56   1  16       N/A 128G hpctpa3pc0005
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ $RX_ROOT/E05/results/report.md
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/results/report.md: line 3: plan.json: command not found
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/results/report.md: line 3: Generated: command not found
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/results/report.md: line 7: syntax error near unexpected token `|'
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/results/report.md: line 7: `| family | macro_AUPRC_lift_over_no_skill | macro_AUPRC_lift_over_rate | macro_AUROC | cohorts_AUROC_above_0.5 |'
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
