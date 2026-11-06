(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next} $h["mode"]=="LFT" && ($h["family"]=="RAND" || $h["family"]=="R"){printf "%-9s %-5s %.3f\n",$h["held_out_cohort"],$h["family"],$h["AUPRC"]}' "$RX_ROOT/E01/results/per_cohort.tsv" | sort
Choueiri  R     0.271
Choueiri  RAND  0.216
Gide      R     0.625
Gide      RAND  0.648
Hugo      R     0.597
Hugo      RAND  0.524
Kim       R     0.614
Kim       RAND  0.399
Riaz      R     0.284
Riaz      RAND  0.317
Rose      R     0.270
Rose      RAND  0.181
Snyder    R     0.284
Snyder    RAND  0.310
Zhao      R     0.714
Zhao      RAND  0.563
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cat "$RX_ROOT/E02/results/report.md" "$RX_ROOT/E04/results/report.md"
# E02: Variance decomposition: strategy vs pretraining seed vs fine-tuning seed vs cohort

Generated 2026-11-05T23:24:59+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

## LFT

Primary model: AUPRC ~ strategy + (1|checkpoint) + (1|fine-tuning seed) + (1|cohort), REML, 360 cohort-level fits; 500 parametric bootstrap refits.

| component | variance | share | share_ci95_low | share_ci95_high |
|---|---|---|---|---|
| strategy (fixed) | 0.0000 | 0.0009 | 0.0002 | 0.0212 |
| checkpoint | 0.0008 | 0.0193 | 0.0011 | 0.0623 |
| fine_tuning_seed | 0.0000 | 0.0000 | 0.0000 | 0.0082 |
| cohort | 0.0290 | 0.7421 | 0.4279 | 0.8636 |
| residual | 0.0093 | 0.2377 | 0.1270 | 0.5324 |

Extended and cohort-averaged models are in variance_components.tsv.

Plain statement (LFT): pretraining seed explains 1.9% of cohort-level AUPRC variance; strategy explains 0.1%; held-out cohort 74.2%; fine-tuning seed 0.0%; residual (fine-tuning noise within checkpoint x cohort) 23.8%.

## PFT

Primary model: AUPRC ~ strategy + (1|checkpoint) + (1|fine-tuning seed) + (1|cohort), REML, 360 cohort-level fits; 500 parametric bootstrap refits.

| component | variance | share | share_ci95_low | share_ci95_high |
|---|---|---|---|---|
| strategy (fixed) | 0.0000 | 0.0006 | 0.0001 | 0.0204 |
| checkpoint | 0.0007 | 0.0188 | 0.0004 | 0.0612 |
| fine_tuning_seed | 0.0000 | 0.0000 | 0.0000 | 0.0086 |
| cohort | 0.0273 | 0.7273 | 0.4079 | 0.8542 |
| residual | 0.0095 | 0.2534 | 0.1365 | 0.5559 |

Extended and cohort-averaged models are in variance_components.tsv.

Plain statement (PFT): pretraining seed explains 1.9% of cohort-level AUPRC variance; strategy explains 0.1%; held-out cohort 72.7%; fine-tuning seed 0.0%; residual (fine-tuning noise within checkpoint x cohort) 25.3%.

Caveat: five pretraining seeds and three strategies give few levels for the checkpoint and fixed components; the bootstrap intervals, not the point shares, carry that uncertainty. Cohort is treated as random to describe heterogeneity, not to generalize beyond these eight studies.
# E04: Exact bootstrap intervals, TOST equivalence and required sample size

Generated 2026-11-05T22:43:27+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

Stock-finalizer contrast bounds reproduced for 24/24 rows (tolerance 1e-9); all intervals below use those same draws.

## LFT

Primary margin: M2_half_published_skill = 0.0782 (0.5 x (published macro AUPRC 0.5250 - no-skill 0.3685))

| contrast | scope | estimate | ci90_low | ci90_high | conclusion | p_tost | power_if_true_difference_zero | required_patients_if_zero | required_cohorts_if_zero |
|---|---|---|---|---|---|---|---|---|---|
| federation_C_U_minus_B_U | patient_within_fixed_cohorts | -0.0005 | -0.0262 | 0.0253 | equivalent_within_margin | 0.0000 | 0.9991 | 121 |  |
| federation_C_U_minus_B_U | cohort_and_patient | -0.0005 | -0.0362 | 0.0326 | equivalent_within_margin | 0.0000 | 0.9646 |  | 5 |
| strategy_C_U_minus_A_U | patient_within_fixed_cohorts | -0.0126 | -0.0480 | 0.0158 | equivalent_within_margin | 0.0007 | 0.9832 | 182 |  |
| strategy_C_U_minus_A_U | cohort_and_patient | -0.0126 | -0.0587 | 0.0271 | equivalent_within_margin | 0.0080 | 0.8219 |  | 8 |
| gtex_B_U_minus_A_U | patient_within_fixed_cohorts | -0.0122 | -0.0432 | 0.0134 | equivalent_within_margin | 0.0004 | 0.9959 | 146 |  |
| gtex_B_U_minus_A_U | cohort_and_patient | -0.0122 | -0.0571 | 0.0278 | equivalent_within_margin | 0.0087 | 0.8385 |  | 8 |
| A_U_minus_R | patient_within_fixed_cohorts | -0.0451 | -0.0821 | 0.0037 | inconclusive_interval_crosses_margin | 0.0674 | 0.8155 | 336 |  |
| A_U_minus_R | cohort_and_patient | -0.0451 | -0.1264 | 0.0374 | inconclusive_interval_crosses_margin | 0.2129 | 0.0000 |  | 28 |
| B_U_minus_R | patient_within_fixed_cohorts | -0.0573 | -0.0969 | -0.0106 | inconclusive_interval_crosses_margin | 0.1716 | 0.8098 | 340 |  |
| B_U_minus_R | cohort_and_patient | -0.0573 | -0.1416 | 0.0314 | inconclusive_interval_crosses_margin | 0.3079 | 0.0000 |  | 32 |
| C_U_minus_R | patient_within_fixed_cohorts | -0.0577 | -0.1020 | -0.0075 | inconclusive_interval_crosses_margin | 0.2001 | 0.7124 | 404 |  |
| C_U_minus_R | cohort_and_patient | -0.0577 | -0.1338 | 0.0202 | inconclusive_interval_crosses_margin | 0.2928 | 0.0238 |  | 25 |

## PFT

Primary margin: M2_half_published_skill = 0.0750 (0.5 x (published macro AUPRC 0.5186 - no-skill 0.3685))

| contrast | scope | estimate | ci90_low | ci90_high | conclusion | p_tost | power_if_true_difference_zero | required_patients_if_zero | required_cohorts_if_zero |
|---|---|---|---|---|---|---|---|---|---|
| federation_C_U_minus_B_U | patient_within_fixed_cohorts | 0.0012 | -0.0250 | 0.0303 | equivalent_within_margin | 0.0000 | 0.9958 | 147 |  |
| federation_C_U_minus_B_U | cohort_and_patient | 0.0012 | -0.0362 | 0.0391 | equivalent_within_margin | 0.0006 | 0.8994 |  | 7 |
| strategy_C_U_minus_A_U | patient_within_fixed_cohorts | -0.0095 | -0.0426 | 0.0211 | equivalent_within_margin | 0.0005 | 0.9751 | 197 |  |
| strategy_C_U_minus_A_U | cohort_and_patient | -0.0095 | -0.0538 | 0.0300 | equivalent_within_margin | 0.0081 | 0.8018 |  | 8 |
| gtex_B_U_minus_A_U | patient_within_fixed_cohorts | -0.0107 | -0.0393 | 0.0133 | equivalent_within_margin | 0.0001 | 0.9973 | 138 |  |
| gtex_B_U_minus_A_U | cohort_and_patient | -0.0107 | -0.0550 | 0.0298 | equivalent_within_margin | 0.0095 | 0.7975 |  | 9 |
| A_U_minus_R | patient_within_fixed_cohorts | -0.0319 | -0.0662 | 0.0183 | equivalent_within_margin | 0.0259 | 0.7919 | 352 |  |
| A_U_minus_R | cohort_and_patient | -0.0319 | -0.1169 | 0.0545 | inconclusive_interval_crosses_margin | 0.1675 | 0.0000 |  | 34 |
| B_U_minus_R | patient_within_fixed_cohorts | -0.0426 | -0.0778 | 0.0041 | inconclusive_interval_crosses_margin | 0.0604 | 0.8275 | 328 |  |
| B_U_minus_R | cohort_and_patient | -0.0426 | -0.1333 | 0.0510 | inconclusive_interval_crosses_margin | 0.2373 | 0.0000 |  | 39 |
| C_U_minus_R | patient_within_fixed_cohorts | -0.0414 | -0.0821 | 0.0132 | inconclusive_interval_crosses_margin | 0.0782 | 0.6586 | 440 |  |
| C_U_minus_R | cohort_and_patient | -0.0414 | -0.1241 | 0.0458 | inconclusive_interval_crosses_margin | 0.2084 | 0.0000 |  | 33 |

Equivalence requires the 90% interval inside (-margin, +margin). An interval crossing a margin is inconclusive, not evidence of a difference or of similarity. Required sizes assume the bootstrap SE scales as n^(-1/2) (checked in se_scaling_check.tsv) and new patients or cohorts resemble the current ones.
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh --dry-run
mit/E06_federated_compass_recipe.sh
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh            # also starts the Flower server/client jobs immediately

# Cheap GPU work on existing checkpoints (embeddings, head refits)
bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh
bash HPC_reviewer_experiments/submit/E10_biological_agreement.sh
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/plan.json
train                        array[15]    train_gpu      after=-  15 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
recipe-plan                  job          cpu            after=collect  freeze + preflight clinical panel recipe
recipe-owners                array[128]   clinical_gpu   after=recipe-plan  inner selection owners (fine-tuning seed 24)
recipe-remaining             array[256]   clinical_gpu   after=recipe-owners  remaining fine-tuning seeds (cached selection)
recipe-finalize              job          cpu_large      after=recipe-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=recipe-finalize  experiment analysis and report
sbatch --parsable --job-name=rx_E06_train --cpus-per-task=8 --mem=64G --time=3-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-federated/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-14%4 /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E06 train
sbatch --parsable --job-name=rx_E06_collect --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/collect.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<train>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E06 collect
sbatch --parsable --job-name=rx_E06_recipe-plan --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/recipe-plan.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<collect>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E06 recipe-plan
sbatch --parsable --job-name=rx_E06_recipe-owners --cpus-per-task=8 --mem=64G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/recipe-owners.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-127%8 '--dependency=afterok:<recipe-plan>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E06 recipe-owners
sbatch --parsable --job-name=rx_E06_recipe-remaining --cpus-per-task=8 --mem=64G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/recipe-remaining.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-255%8 '--dependency=afterok:<recipe-owners>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E06 recipe-remaining
sbatch --parsable --job-name=rx_E06_recipe-finalize --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/recipe-finalize.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<recipe-remaining>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E06 recipe-finalize
sbatch --parsable --job-name=rx_E06_analyze --cpus-per-task=16 --mem=128G --time=2-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/analyze.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<recipe-finalize>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E06 analyze
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh
train                        array[15]    train_gpu      after=-  15 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
recipe-plan                  job          cpu            after=collect  freeze + preflight clinical panel recipe
recipe-owners                array[128]   clinical_gpu   after=recipe-plan  inner selection owners (fine-tuning seed 24)
recipe-remaining             array[256]   clinical_gpu   after=recipe-owners  remaining fine-tuning seeds (cached selection)
recipe-finalize              job          cpu_large      after=recipe-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=recipe-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/submission_20261106T115519+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/plan.json
deploy                       job          login          after=-  submit the Flower server/client/validation jobs (existing launcher)
simulate                     array[1]     train_gpu      after=-  engine twin with Flower random streams
benchmark                    job          cpu            after=simulate  sacct cost, telemetry and parity
'# login stage' deploy
sbatch --parsable --job-name=rx_E11_simulate --cpus-per-task=8 --mem=64G --time=3-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/logs/simulate.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-federated/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-0%4 /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E11 simulate
sbatch --parsable --job-name=rx_E11_benchmark --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/logs/benchmark.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<login>:<simulate>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E11 benchmark
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh            # also starts the Flower server/client jobs immediately
deploy                       job          login          after=-  submit the Flower server/client/validation jobs (existing launcher)
simulate                     array[1]     train_gpu      after=-  engine twin with Flower random streams
benchmark                    job          cpu            after=simulate  sacct cost, telemetry and parity


Traceback (most recent call last):
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_train/federated_test/scripts/09_run_protocol_v2_task.py", line 46, in <module>
    main()
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_train/federated_test/scripts/09_run_protocol_v2_task.py", line 35, in main
    verify_bindings(task["inputs"])
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_train/centralized_test/scripts/training_protocol.py", line 42, in verify_bindings
    raise ValueError(f"Frozen input changed: {name}")
ValueError: Frozen input changed: repository:compass_hpc_foundation_model_test/scripts/01_download_clinical_cohorts.py
Traceback (most recent call last):
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rx.py", line 76, in <module>
    raise SystemExit(main())
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rx.py", line 59, in main
    receipt = orchestrate.submit(args.experiment, dry_run=args.dry_run, start=args.from_stage, only=args.only,
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/orchestrate.py", line 186, in submit
    jobs[stage.name] = module(ctx.experiment).run_login_stage(ctx, stage.name)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/experiments/e11_hpc_deployment.py", line 94, in run_login_stage
    subprocess.run([str(python), str(FEDERATED_SCRIPTS / "09_run_protocol_v2_task.py"), "--task-spec", deployment["spec"],
  File "/home/4475918/.conda/envs/compass-foundation-test/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/home/4475918/.conda/envs/compass-federated/bin/python', '/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_train/federated_test/scripts/09_run_protocol_v2_task.py', '--task-spec', '/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/deploy/C_U_seed17.deployed.task.json', '--expected-sha256', 'eb8c1a6be96571aedbd2871ce6b146064dfd756a8beb1cc34903e50e7bbc9aec']' returned non-zero exit status 1.
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ # Cheap GPU work on existing checkpoints (embeddings, head refits)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E03/plan.json
predictions                  job          cpu_large      after=-  probability/rank ensembles with paired bootstrap
embed                        array[16]    embed_gpu      after=-  frozen concept embeddings of the clinical cohorts
embeddings                   job          cpu_large      after=predictions,embed  nested LOCO logistic probes on single vs ensembled embeddings; report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E03/submission_20261106T115535+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E10_biological_agreement.sh
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E10/plan.json
embed                        array[16]    embed_gpu      after=-  concept embeddings: ICB patients and probe rows
attribution                  array[16]    clinical_gpu   after=-  refit LFT heads, check reproduction, concept Shapley values
analyze                      job          cpu_large      after=embed,attribution  CKA vs seed baseline, attribution agreement, report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E10/submission_20261106T115536+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06
train                        complete 0/15  failed 0  running 4
collect                      complete 0/1  failed 0  running 0
recipe-plan                  complete 0/1  failed 0  running 0
recipe-owners                complete 0/128  failed 0  running 0
recipe-remaining             complete 0/256  failed 0  running 0
recipe-finalize              complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -20 "$RX_ROOT"/E06/logs/train.*_0.log     # should print one "epoch NNN: train=... val_context_macro=..." line per epoch
lgorithms E12_prrx stage E06/train[0] on hpctpa3pc0001 job 21774240 python /home/4475918/.conda/envs/compass-federated/bin/python
ivacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh
done(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for s in E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
>   bash HPC_reviewer_experiments/submit/$s.sh
> done
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/plan.json
train                        array[38]    train_gpu      after=-  38 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
exposure-plan                job          cpu            after=collect  freeze + preflight clinical panel exposure
exposure-owners              array[312]   clinical_gpu   after=exposure-plan  inner selection owners (fine-tuning seed 24)
exposure-remaining           array[624]   clinical_gpu   after=exposure-owners  remaining fine-tuning seeds (cached selection)
exposure-finalize            job          cpu_large      after=exposure-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=exposure-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/submission_20261106T115607+0000.json
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08/plan.json
train                        array[27]    train_gpu      after=-  27 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
partitions-plan              job          cpu            after=collect  freeze + preflight clinical panel partitions
partitions-owners            array[224]   clinical_gpu   after=partitions-plan  inner selection owners (fine-tuning seed 24)
partitions-remaining         array[448]   clinical_gpu   after=partitions-owners  remaining fine-tuning seeds (cached selection)
partitions-finalize          job          cpu_large      after=partitions-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=partitions-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08/submission_20261106T115608+0000.json
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08B/plan.json
train                        array[24]    train_gpu      after=-  24 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
algorithms-plan              job          cpu            after=collect  freeze + preflight clinical panel algorithms
algorithms-owners            array[200]   clinical_gpu   after=algorithms-plan  inner selection owners (fine-tuning seed 24)
algorithms-remaining         array[400]   clinical_gpu   after=algorithms-owners  remaining fine-tuning seeds (cached selection)
algorithms-finalize          job          cpu_large      after=algorithms-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=algorithms-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08B/submission_20261106T115609+0000.json
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E12/plan.json
train                        array[18]    train_gpu      after=-  18 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
attack-mia                   array[18]    train_gpu      after=train  membership inference on the final-round updates
attack-inversion             array[6]     train_gpu      after=train  gradient inversion of one DP-processed local step
privacy-plan                 job          cpu            after=collect  freeze + preflight clinical panel privacy
privacy-owners               array[152]   clinical_gpu   after=privacy-plan  inner selection owners (fine-tuning seed 24)
privacy-remaining            array[304]   clinical_gpu   after=privacy-owners  remaining fine-tuning seeds (cached selection)
privacy-finalize             job          cpu_large      after=privacy-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=privacy-finalize,attack-mia,attack-inversion  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E12/submission_20261106T115609+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
