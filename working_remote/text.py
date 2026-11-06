(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next} $h["contrast"]=="federation_C_U_minus_B_U"{printf "%s %-28s %-26s %.3f [%.4f, %.4f] %s\n",$h["mode"],$h["scope"],$h["margin_id"],$h["margin"],$h["ci90_low"],$h["ci90_high"],$h["conclusion"]}' "$RX_ROOT/E04/results/tost.tsv"
urce hpc/site.env; set +a
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E11 --force-new     # E11 never submitted, so re-planning is allowed
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh
grep -E '"code_inputs_rebound"|"run_dir"' "$RX_ROOT/E11/deploy/deployments.json"
squeue -u LFT patient_within_fixed_cohorts M2_half_published_skill    0.078 [-0.0262, 0.0253] equivalent_within_margin
LFT patient_within_fixed_cohorts M2_quarter_published_skill 0.039 [-0.0262, 0.0253] equivalent_within_margin
LFT patient_within_fixed_cohorts fixed_0.05                 0.050 [-0.0262, 0.0253] equivalent_within_margin
LFT patient_within_fixed_cohorts fixed_0.03                 0.030 [-0.0262, 0.0253] equivalent_within_margin
LFT patient_within_fixed_cohorts fixed_0.02                 0.020 [-0.0262, 0.0253] inconclusive_interval_crosses_margin
LFT cohort_and_patient           M2_half_published_skill    0.078 [-0.0362, 0.0326] equivalent_within_margin
LFT cohort_and_patient           M2_quarter_published_skill 0.039 [-0.0362, 0.0326] equivalent_within_margin
LFT cohort_and_patient           fixed_0.05                 0.050 [-0.0362, 0.0326] equivalent_within_margin
LFT cohort_and_patient           fixed_0.03                 0.030 [-0.0362, 0.0326] inconclusive_interval_crosses_margin
LFT cohort_and_patient           fixed_0.02                 0.020 [-0.0362, 0.0326] inconclusive_interval_crosses_margin
PFT patient_within_fixed_cohorts M2_half_published_skill    0.075 [-0.0250, 0.0303] equivalent_within_margin
PFT patient_within_fixed_cohorts M2_quarter_published_skill 0.038 [-0.0250, 0.0303] equivalent_within_margin
PFT patient_within_fixed_cohorts fixed_0.05                 0.050 [-0.0250, 0.0303] equivalent_within_margin
PFT patient_within_fixed_cohorts fixed_0.03                 0.030 [-0.0250, 0.0303] noninferior_not_equivalent
PFT patient_within_fixed_cohorts fixed_0.02                 0.020 [-0.0250, 0.0303] inconclusive_interval_crosses_margin
PFT cohort_and_patient           M2_half_published_skill    0.075 [-0.0362, 0.0391] equivalent_within_margin
PFT cohort_and_patient           M2_quarter_published_skill 0.038 [-0.0362, 0.0391] noninferior_not_equivalent
PFT cohort_and_patient           fixed_0.05                 0.050 [-0.0362, 0.0391] equivalent_within_margin
PFT cohort_and_patient           fixed_0.03                 0.030 [-0.0362, 0.0391] inconclusive_interval_crosses_margin
PFT cohort_and_patient           fixed_0.02                 0.020 [-0.0362, 0.0391] inconclusive_interval_crosses_margin
"$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val     # the Flower pipeline jobs


tail -5 "$RX_ROOT"/E06/logs/train.*_0.log      # expect "CR_CEN seed 17 epoch 001: trai(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
n=... val_context_macro=..."
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06

squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scancel

squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol hold
# later:
squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git pull --ff-only
Already up to date.
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E11 --force-new     # E11 never submitted, so re-planning is allowed

/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/plan.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh --dry-run
deploy                       job          login          after=-  submit the Flower server/client/validation jobs (existing launcher)
simulate                     array[1]     train_gpu      after=-  engine twin with Flower random streams
benchmark                    job          cpu            after=simulate  sacct cost, telemetry and parity
'# login stage' deploy
sbatch --parsable --job-name=rx_E11_simulate --cpus-per-task=8 --mem=64G --time=3-00:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/logs/simulate.%A_%a.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-federated/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --gres=gpu:1 --partition=red --account=paulocilas.moraislyra --qos=medium --array=0-0%4 /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_array.sbatch E11 simulate
sbatch --parsable --job-name=rx_E11_benchmark --cpus-per-task=4 --mem=32G --time=08:00:00 --output=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/logs/benchmark.%j.log --export=ALL,RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python,RX_REPO=/share/lab_goecks/paulo/federated-learning-model,RX_ROOT=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105 --partition=red --account=paulocilas.moraislyra --qos=medium '--dependency=afterok:<login>:<simulate>' /share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch E11 benchmark
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh
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
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ grep -E '"code_inputs_rebound"|"run_dir"' "$RX_ROOT/E11/deploy/deployments.json"
      "run_dir": "/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/launch_fix_20261019T014157Z/federated_project/runs/rx_E11_deployed_seed17_9feb3f9713",
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val     # the Flower pipeline jobs
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -5 "$RX_ROOT"/E06/logs/train.*_0.log      # expect "CR_CEN seed 17 epoch 001: train=... val_context_macro=..."
rx stage E06/train[0] on hpctpa3pc0001 job 21774240 python /home/4475918/.conda/envs/compass-federated/bin/python
CR_CEN seed 17 epoch 001: train=0.800003 val_context_macro=0.557252
CR_CEN seed 17 epoch 002: train=0.517616 val_context_macro=0.471781
CR_CEN seed 17 epoch 003: train=0.474076 val_context_macro=0.436704
CR_CEN seed 17 epoch 004: train=0.436836 val_context_macro=0.405692
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06
train                        complete 0/15  failed 0  running 4
collect                      complete 0/1  failed 0  running 0
recipe-plan                  complete 0/1  failed 0  running 0
recipe-owners                complete 0/128  failed 0  running 0
recipe-remaining             complete 0/256  failed 0  running 0
recipe-finalize              complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scancel
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol hold
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ # later:
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
21774259_[10-15%8]  red rx_E10_attri  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
          21774294  red rx_E12_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774293  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774285  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774284  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774278  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774277  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774271  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774270  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774260  red rx_E10_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774253  red rx_E03_embed  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
          21774246  red rx_E06_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774245  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
21774292_[0-303%8]  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774291_[0-151%8]  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774290  red rx_E12_priva  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
  21774289_[0-5%4]  red rx_E12_attac  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (DependencyNeverSatisfied)
 21774288_[0-17%4]  red rx_E12_attac  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (DependencyNeverSatisfied)
          21774287  red rx_E12_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (DependencyNeverSatisfied)
21774283_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774282_[0-199%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774281  red rx_E08B_algo  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774280  red rx_E08B_coll  4475918 PD       0:00    8:00:00   1   4       N/A  32G (DependencyNeverSatisfied)
21774276_[0-447%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774275_[0-223%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774274  red rx_E08_parti  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774273  red rx_E08_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (DependencyNeverSatisfied)
21774269_[0-623%8]  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774268_[0-311%8]  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774267  red rx_E07_expos  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774266  red rx_E07_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (DependencyNeverSatisfied)
21774244_[0-255%8]  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774243_[0-127%8]  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774242  red rx_E06_recip  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774241  red rx_E06_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (DependencyNeverSatisfied)
        21774259_3  red rx_E10_attri  4475918  R      10:46 1-23:49:14   1   8 gres/gpu:  64G hpctpa3pc0051
        21774259_2  red rx_E10_attri  4475918  R      11:42 1-23:48:18   1   8 gres/gpu:  64G hpctpa3pc0066
        21774259_6  red rx_E10_attri  4475918  R       0:16 1-23:59:44   1   8 gres/gpu:  64G hpctpa3pc0008
        21774259_7  red rx_E10_attri  4475918  R       0:16 1-23:59:44   1   8 gres/gpu:  64G hpctpa3pc0039
        21774259_8  red rx_E10_attri  4475918  R       0:16 1-23:59:44   1   8 gres/gpu:  64G hpctpa3pc0030
        21774259_9  red rx_E10_attri  4475918  R       0:16 1-23:59:44   1   8 gres/gpu:  64G hpctpa3pc0001
        21774259_5  red rx_E10_attri  4475918  R       0:35 1-23:59:25   1   8 gres/gpu:  64G hpctpa3pc0068
        21774259_4  red rx_E10_attri  4475918  R       0:41 1-23:59:19   1   8 gres/gpu:  64G hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
