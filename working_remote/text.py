(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
 --ff-only
git log -1 --oneline                  # expect: e73c6d5 bug fix E11

squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o "%A %j" | sort -u
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git pull --ff-only
remote: Enumerating objects: 26, done.
remote: Counting objects: 100% (26/26), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 16 (delta 13), reused 16 (delta 13), pack-reused 0 (from 0)
Unpacking objects: 100% (16/16), 3.65 KiB | 22.00 KiB/s, done.
From github.com:paulocilasjr/federated-learning-model
   f29529a..e73c6d5  main       -> origin/main
Updating f29529a..e73c6d5
Fast-forward
 HPC_reviewer_experiments/rexp/analysis.py                       |  3 ++-
 HPC_reviewer_experiments/rexp/experiments/e11_hpc_deployment.py | 35 +++++++++++++++++++++++++++++-
 HPC_reviewer_experiments/rexp/orchestrate.py                    | 16 +++++++++++++-
 HPC_reviewer_experiments/tests/test_bootstrap_reproduction.py   | 11 ++++++++++
 HPC_reviewer_experiments/tests/test_orchestration.py            | 36 ++++++++++++++++++++++++++++++-
 5 files changed, 97 insertions(+), 4 deletions(-)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git log -1 --oneline                  # expect: e73c6d5 bug fix E11
e73c6d5 (HEAD -> main, origin/main, origin/HEAD) bug fix E11
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E06_train,rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o "%A %j" | sort -u
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -o "%A %j" | awk '$2 ~ /^rx_E(06|07|08|08B|12)_/ {print $1}' | sort -u | xargs -r scancel
or s in E06_federated_compass_recipe E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh --from-stage train --allow-code-change
done(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for s in E06_federated_compass_reci07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
>   bash HPC_reviewer_experiments/submit/$s.sh --from-stage train --allow-code-change
> done
train                        array[15]    train_gpu      after=-  15 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
recipe-plan                  job          cpu            after=collect  freeze + preflight clinical panel recipe
recipe-owners                array[128]   clinical_gpu   after=recipe-plan  inner selection owners (fine-tuning seed 24)
recipe-remaining             array[256]   clinical_gpu   after=recipe-owners  remaining fine-tuning seeds (cached selection)
recipe-finalize              job          cpu_large      after=recipe-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=recipe-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/submission_20261106T121958+0000.json
train                        array[38]    train_gpu      after=-  38 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
exposure-plan                job          cpu            after=collect  freeze + preflight clinical panel exposure
exposure-owners              array[312]   clinical_gpu   after=exposure-plan  inner selection owners (fine-tuning seed 24)
exposure-remaining           array[624]   clinical_gpu   after=exposure-owners  remaining fine-tuning seeds (cached selection)
exposure-finalize            job          cpu_large      after=exposure-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=exposure-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/submission_20261106T121958+0000.json
train                        array[27]    train_gpu      after=-  27 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
partitions-plan              job          cpu            after=collect  freeze + preflight clinical panel partitions
partitions-owners            array[224]   clinical_gpu   after=partitions-plan  inner selection owners (fine-tuning seed 24)
partitions-remaining         array[448]   clinical_gpu   after=partitions-owners  remaining fine-tuning seeds (cached selection)
partitions-finalize          job          cpu_large      after=partitions-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=partitions-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08/submission_20261106T122000+0000.json
train                        array[24]    train_gpu      after=-  24 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
algorithms-plan              job          cpu            after=collect  freeze + preflight clinical panel algorithms
algorithms-owners            array[200]   clinical_gpu   after=algorithms-plan  inner selection owners (fine-tuning seed 24)
algorithms-remaining         array[400]   clinical_gpu   after=algorithms-owners  remaining fine-tuning seeds (cached selection)
algorithms-finalize          job          cpu_large      after=algorithms-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=algorithms-finalize  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E08B/submission_20261106T122000+0000.json
train                        array[18]    train_gpu      after=-  18 foundation runs (engine)
collect                      job          cpu            after=train  verify runs, load checkpoints, write models.tsv with R
attack-mia                   array[18]    train_gpu      after=train  membership inference on the final-round updates
attack-inversion             array[6]     train_gpu      after=train  gradient inversion of one DP-processed local step
privacy-plan                 job          cpu            after=collect  freeze + preflight clinical panel privacy
privacy-owners               array[152]   clinical_gpu   after=privacy-plan  inner selection owners (fine-tuning seed 24)
privacy-remaining            array[304]   clinical_gpu   after=privacy-owners  remaining fine-tuning seeds (cached selection)
privacy-finalize             job          cpu_large      after=privacy-remaining  stock verification + paired bootstrap
analyze                      job          cpu_large      after=privacy-finalize,attack-mia,attack-inversion  experiment analysis and report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E12/submission_20261106T122001+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$   "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E11 --force-new
ments/submit/E11_hpc_deployment.sh
grep '"code_inputs_rebound"' "$RX_ROOT/E11/deploy/deployments.json"          # should be a number > 0
squeue -u "$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val   # the Flower server/client/validation jobs

/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/plan.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E11_hpc_deployment.sh
deploy                       job          login          after=-  submit the Flower server/client/validation jobs (existing launcher)
simulate                     array[1]     train_gpu      after=-  engine twin with Flower random streams
benchmark                    job          cpu            after=simulate  sacct cost, telemetry and parity
Runtime check OK: Flower 1.8.0 PyTorch 1.13.1
Separate TCGA/GTEx client data already complete; skipping preparation.
Flower server:       21774380
TCGA + GTEx clients: 21774381
Validate checkpoint: 21774382
Run tag:             rx_E11_deployed_seed17_9feb3f9713
Rounds:              100
Initialization:       scratch
Training negatives:   random_within_context
GTEx donor fraction:  1.0
Matched round anchors: 27648
Final model:         /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/launch_fix_20261019T014157Z/federated_project/runs/rx_E11_deployed_seed17_9feb3f9713/pretrainer_federated_tcga_gtex.pt
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/submission_20261106T122016+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ grep '"code_inputs_rebound"' "$RX_ROOT/E11/deploy/deployments.json"          # should be a number > 0
      "code_inputs_rebound": 7,
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -n compass_fl_data,compass_fl_srv,compass_fl_cli,compass_fl_val   # the Flower server/client/validation jobs
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21774382  red compass_fl_v  4475918 PD       0:00    2:00:00   1   2       N/A  32G (Dependency)
    21774381_[0-1]  red compass_fl_c  4475918 PD       0:00 7-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774380  red compass_fl_s  4475918 PD       0:00 7-00:00:00   1   2       N/A  16G (Priority)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E03
s/*.log | xargs -r tail -n 4predictions                  complete 0/1  failed 1  running 0
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ grep -l Traceback "$RX_ROOT"/E03/logs/*.log | xargs -r tail -n 4
    seed_level = seed_effects(panel, d, mode, terms)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/analysis.py", line 50, in seed_effects
    shared = sorted(set.intersection(*varying), key=int) if varying else []
ValueError: invalid literal for int() with base 10: 'ensemble'
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -o "%A %j" | awk '$2 ~ /^rx_E03_/ {print $1}' | sort -u | xargs -r scancel
bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh --only predictions embeddings --allow-code-change
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh --only predictions embeddings --allow-code-change
predictions                  job          cpu_large      after=-  probability/rank ensembles with paired bootstrap
embed                        array[16]    embed_gpu      after=-  frozen concept embeddings of the clinical cohorts
embeddings                   job          cpu_large      after=predictions,embed  nested LOCO logistic probes on single vs ensembled embeddings; report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E03/submission_20261106T122113+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for e in E03 E06 E07 E08 E08B E10 E11 E12; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
== E03
predictions                  complete 0/1  failed 0  running 1
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 0/1  failed 0  running 0
== E06
train                        complete 0/15  failed 0  running 4
collect                      complete 0/1  failed 0  running 0
recipe-plan                  complete 0/1  failed 0  running 0
recipe-owners                complete 0/128  failed 0  running 0
recipe-remaining             complete 0/256  failed 0  running 0
recipe-finalize              complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E07
train                        complete 0/38  failed 0  running 0
collect                      complete 0/1  failed 0  running 0
exposure-plan                complete 0/1  failed 0  running 0
exposure-owners              complete 0/312  failed 0  running 0
exposure-remaining           complete 0/624  failed 0  running 0
exposure-finalize            complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E08
train                        complete 0/27  failed 0  running 0
collect                      complete 0/1  failed 0  running 0
partitions-plan              complete 0/1  failed 0  running 0
partitions-owners            complete 0/224  failed 0  running 0
partitions-remaining         complete 0/448  failed 0  running 0
partitions-finalize          complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E08B
train                        complete 0/24  failed 0  running 0
collect                      complete 0/1  failed 0  running 0
algorithms-plan              complete 0/1  failed 0  running 0
algorithms-owners            complete 0/200  failed 0  running 0
algorithms-remaining         complete 0/400  failed 0  running 0
algorithms-finalize          complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E10
embed                        complete 16/16  failed 0  running 0
attribution                  complete 7/16  failed 0  running 8
analyze                      complete 0/1  failed 0  running 0
== E11
deploy                       complete 0/1  failed 0  running 0
simulate                     complete 0/1  failed 0  running 0
benchmark                    complete 0/1  failed 0  running 0
== E12
train                        complete 0/18  failed 0  running 0
collect                      complete 0/1  failed 0  running 0
attack-mia                   complete 0/18  failed 0  running 0
attack-inversion             complete 0/6  failed 0  running 0
privacy-plan                 complete 0/1  failed 0  running 0
privacy-owners               complete 0/152  failed 0  running 0
privacy-remaining            complete 0/304  failed 0  running 0
privacy-finalize             complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -3 "$(ls -t "$RX_ROOT"/E06/logs/train.*_0.log | head -1)"
CR_CEN seed 17 epoch 003: train=0.474076 val_context_macro=0.436704
CR_CEN seed 17 epoch 004: train=0.436836 val_context_macro=0.405692
[2026-11-06T07:11:04.573] error: *** JOB 21774247 ON hpctpa3pc0001 CANCELLED AT 2026-11-06T07:11:04 DUE to SIGNAL Terminated ***
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
       21774259_15  red rx_E10_attri  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
          21774387  red rx_E03_embed  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774375  red rx_E12_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774374  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774366  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774365  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774359  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774358  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774351  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774345  red rx_E06_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774344  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774260  red rx_E10_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
 21774360_[0-23%4]  red rx_E08B_trai  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774367_[0-17%4]  red rx_E12_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
    21774383_[0%4]  red rx_E11_simul  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774353_[0-26%4]  red rx_E08_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774346_[0-37%4]  red rx_E07_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774339_[0-14%4]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
          21774384  red rx_E11_bench  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774382  red compass_fl_v  4475918 PD       0:00    2:00:00   1   2       N/A  32G (Dependency)
    21774381_[0-1]  red compass_fl_c  4475918 PD       0:00 7-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774373_[0-303%8]  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774372_[0-151%8]  red rx_E12_priva  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774371  red rx_E12_priva  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
  21774370_[0-5%4]  red rx_E12_attac  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Dependency)
 21774369_[0-17%4]  red rx_E12_attac  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774368  red rx_E12_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
21774364_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774363_[0-199%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774362  red rx_E08B_algo  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774361  red rx_E08B_coll  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
21774357_[0-447%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774356_[0-223%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774355  red rx_E08_parti  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774354  red rx_E08_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
21774350_[0-623%8]  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774349_[0-311%8]  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774348  red rx_E07_expos  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774347  red rx_E07_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
21774343_[0-255%8]  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774342_[0-127%8]  red rx_E06_recip  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
          21774341  red rx_E06_recip  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774340  red rx_E06_colle  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
       21774259_14  red rx_E10_attri  4475918  R       0:23 1-23:59:37   1   8 gres/gpu:  64G hpctpa3pc0068
       21774259_13  red rx_E10_attri  4475918  R       0:44 1-23:59:16   1   8 gres/gpu:  64G hpctpa3pc0055
       21774259_12  red rx_E10_attri  4475918  R       1:08 1-23:58:52   1   8 gres/gpu:  64G hpctpa3pc0001
       21774259_11  red rx_E10_attri  4475918  R       3:43 1-23:56:17   1   8 gres/gpu:  64G hpctpa3pc0066
       21774259_10  red rx_E10_attri  4475918  R       7:11 1-23:52:49   1   8 gres/gpu:  64G hpctpa3pc0051
        21774259_6  red rx_E10_attri  4475918  R      10:20 1-23:49:40   1   8 gres/gpu:  64G hpctpa3pc0008
        21774259_7  red rx_E10_attri  4475918  R      10:20 1-23:49:40   1   8 gres/gpu:  64G hpctpa3pc0039
        21774259_8  red rx_E10_attri  4475918  R      10:20 1-23:49:40   1   8 gres/gpu:  64G hpctpa3pc0030
          21774386  red rx_E03_predi  4475918  R       0:13 1-23:59:47   1  16       N/A 128G hpctpa3pc0024
          21774380  red compass_fl_s  4475918  R       0:05 6-23:59:55   1   2       N/A  16G hpctpa3pc0024
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
