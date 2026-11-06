(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21774339_[4-14%4]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
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
          21774384  red rx_E11_bench  4475918 PD       0:00    8:00:00   1   4       N/A  32G (Dependency)
          21774382  red compass_fl_v  4475918 PD       0:00    2:00:00   1   2       N/A  32G (Dependency)
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
 21774346_[2-37%4]  red rx_E07_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobHeldUser)
 21774367_[0-17%4]  red rx_E12_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobHeldUser)
 21774360_[0-23%4]  red rx_E08B_trai  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobHeldUser)
 21774353_[0-26%4]  red rx_E08_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobHeldUser)
        21774383_0  red rx_E11_simul  4475918  R    1:16:06 2-22:43:54   1   8 gres/gpu:  64G hpctpa3pc0008
        21774381_0  red compass_fl_c  4475918  R    1:16:04 6-22:43:56   1   8 gres/gpu:  64G hpctpa3pc0066
        21774339_3  red rx_E06_train  4475918  R    1:27:12 2-22:32:48   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R    1:29:46 2-22:30:14   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R    1:31:51 2-22:28:09   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R    1:32:46 2-22:27:14   1   8 gres/gpu:  64G hpctpa3pc0030
          21774380  red compass_fl_s  4475918  R    1:39:20 6-22:20:40   1   2       N/A  16G hpctpa3pc0024
        21774381_1  red compass_fl_c  4475918  R       1:39 6-23:58:21   1   8 gres/gpu:  64G hpctpa3pc0055
        21774346_1  red rx_E07_train  4475918  R    1:24:19 2-22:35:41   1   8 gres/gpu:  64G hpctpa3pc0068
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for e in E01 E02 E03 E04 E05 E06 E07 E08 E08B E10 E11 E12; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
== E01
build                        complete 1/1  failed 0  running 0
rand-plan                    complete 1/1  failed 0  running 0
rand-owners                  complete 48/48  failed 0  running 0
rand-remaining               complete 96/96  failed 0  running 0
rand-finalize                complete 1/1  failed 0  running 0
analyze                      complete 1/1  failed 0  running 0
== E02
analyze                      complete 1/1  failed 0  running 0
== E03
predictions                  complete 1/1  failed 0  running 0
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 1/1  failed 0  running 0
== E04
analyze                      complete 1/1  failed 0  running 0
== E05
analyze                      complete 1/1  failed 0  running 0
== E06
train                        complete 0/15  failed 0  running 4
collect                      complete 0/1  failed 0  running 0
recipe-plan                  complete 0/1  failed 0  running 0
recipe-owners                complete 0/128  failed 0  running 0
recipe-remaining             complete 0/256  failed 0  running 0
recipe-finalize              complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E07
train                        complete 1/38  failed 0  running 1
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
attribution                  complete 16/16  failed 0  running 0
analyze                      complete 1/1  failed 0  running 0
== E11
deploy                       complete 0/1  failed 0  running 0
simulate                     complete 0/1  failed 0  running 1
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
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -o "%.18i %.24j %.9T %.11M %.4D %R"
             JOBID                     NAME     STATE        TIME NODE NODELIST(REASON)
 21774339_[4-14%4]             rx_E06_train   PENDING        0:00    1 (JobArrayTaskLimit)
          21774375           rx_E12_analyze   PENDING        0:00    1 (Dependency)
          21774374  rx_E12_privacy-finalize   PENDING        0:00    1 (Dependency)
          21774366          rx_E08B_analyze   PENDING        0:00    1 (Dependency)
          21774365 rx_E08B_algorithms-final   PENDING        0:00    1 (Dependency)
          21774359           rx_E08_analyze   PENDING        0:00    1 (Dependency)
          21774358 rx_E08_partitions-finali   PENDING        0:00    1 (Dependency)
          21774352           rx_E07_analyze   PENDING        0:00    1 (Dependency)
          21774351 rx_E07_exposure-finalize   PENDING        0:00    1 (Dependency)
          21774345           rx_E06_analyze   PENDING        0:00    1 (Dependency)
          21774344   rx_E06_recipe-finalize   PENDING        0:00    1 (Dependency)
          21774384         rx_E11_benchmark   PENDING        0:00    1 (Dependency)
          21774382           compass_fl_val   PENDING        0:00    1 (Dependency)
21774373_[0-303%8] rx_E12_privacy-remaining   PENDING        0:00    1 (Dependency)
21774372_[0-151%8]    rx_E12_privacy-owners   PENDING        0:00    1 (Dependency)
          21774371      rx_E12_privacy-plan   PENDING        0:00    1 (Dependency)
  21774370_[0-5%4]  rx_E12_attack-inversion   PENDING        0:00    1 (Dependency)
 21774369_[0-17%4]        rx_E12_attack-mia   PENDING        0:00    1 (Dependency)
          21774368           rx_E12_collect   PENDING        0:00    1 (Dependency)
21774364_[0-399%8] rx_E08B_algorithms-remai   PENDING        0:00    1 (Dependency)
21774363_[0-199%8] rx_E08B_algorithms-owner   PENDING        0:00    1 (Dependency)
          21774362  rx_E08B_algorithms-plan   PENDING        0:00    1 (Dependency)
          21774361          rx_E08B_collect   PENDING        0:00    1 (Dependency)
21774357_[0-447%8] rx_E08_partitions-remain   PENDING        0:00    1 (Dependency)
21774356_[0-223%8] rx_E08_partitions-owners   PENDING        0:00    1 (Dependency)
          21774355   rx_E08_partitions-plan   PENDING        0:00    1 (Dependency)
          21774354           rx_E08_collect   PENDING        0:00    1 (Dependency)
21774350_[0-623%8] rx_E07_exposure-remainin   PENDING        0:00    1 (Dependency)
21774349_[0-311%8]   rx_E07_exposure-owners   PENDING        0:00    1 (Dependency)
          21774348     rx_E07_exposure-plan   PENDING        0:00    1 (Dependency)
          21774347           rx_E07_collect   PENDING        0:00    1 (Dependency)
21774343_[0-255%8]  rx_E06_recipe-remaining   PENDING        0:00    1 (Dependency)
21774342_[0-127%8]     rx_E06_recipe-owners   PENDING        0:00    1 (Dependency)
          21774341       rx_E06_recipe-plan   PENDING        0:00    1 (Dependency)
          21774340           rx_E06_collect   PENDING        0:00    1 (Dependency)
 21774346_[2-37%4]             rx_E07_train   PENDING        0:00    1 (JobHeldUser)
 21774367_[0-17%4]             rx_E12_train   PENDING        0:00    1 (JobHeldUser)
 21774360_[0-23%4]            rx_E08B_train   PENDING        0:00    1 (JobHeldUser)
 21774353_[0-26%4]             rx_E08_train   PENDING        0:00    1 (JobHeldUser)
        21774383_0          rx_E11_simulate   RUNNING     1:16:41    1 hpctpa3pc0008
        21774381_0           compass_fl_cli   RUNNING     1:16:39    1 hpctpa3pc0066
        21774339_3             rx_E06_train   RUNNING     1:27:47    1 hpctpa3pc0001
        21774339_2             rx_E06_train   RUNNING     1:30:21    1 hpctpa3pc0051
        21774339_1             rx_E06_train   RUNNING     1:32:26    1 hpctpa3pc0039
        21774339_0             rx_E06_train   RUNNING     1:33:21    1 hpctpa3pc0030
          21774380           compass_fl_srv   RUNNING     1:39:55    1 hpctpa3pc0024
        21774381_1           compass_fl_cli   RUNNING        2:14    1 hpctpa3pc0055
        21774346_1             rx_E07_train   RUNNING     1:24:54    1 hpctpa3pc0068
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ ls -t "$RX_ROOT"/E0{6,7,8}*/logs/train.*.log "$RX_ROOT"/E12/logs/train.*.log 2>/dev/null | head -8 | while read f; do echo "== $f"; tail -n 2 "$f"; done
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/train.21774346_1.log
TONLY_X025 seed 42 epoch 098: train=0.252176 val_context_macro=0.333793
TONLY_X025 seed 42 epoch 099: train=0.258321 val_context_macro=0.310768
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774339_0.log
CR_CEN seed 17 epoch 031: train=0.254263 val_context_macro=0.268849
CR_CEN seed 17 epoch 032: train=0.254368 val_context_macro=0.240484
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774339_2.log
CR_CEN seed 42 epoch 030: train=0.255751 val_context_macro=0.268283
CR_CEN seed 42 epoch 031: train=0.252547 val_context_macro=0.279821
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774339_3.log
CR_CEN seed 64 epoch 029: train=0.257811 val_context_macro=0.174616
CR_CEN seed 64 epoch 030: train=0.256341 val_context_macro=0.164476
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/train.21774346_0.log
TONLY_X025 seed 17 epoch 099: train=0.261361 val_context_macro=0.271875
TONLY_X025 seed 17 epoch 100: train=0.254384 val_context_macro=0.252084
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774339_1.log
CR_CEN seed 24 epoch 030: train=0.252762 val_context_macro=0.253425
CR_CEN seed 24 epoch 031: train=0.254034 val_context_macro=0.196817
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774240_0.log
CR_CEN seed 17 epoch 004: train=0.436836 val_context_macro=0.405692
[2026-11-06T07:11:04.573] error: *** JOB 21774247 ON hpctpa3pc0001 CANCELLED AT 2026-11-06T07:11:04 DUE to SIGNAL Terminated ***
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/logs/train.21774240_3.log
CR_CEN seed 64 epoch 004: train=0.434444 val_context_macro=0.324201
[2026-11-06T07:11:04.575] error: *** JOB 21774250 ON hpctpa3pc0039 CANCELLED AT 2026-11-06T07:11:04 DUE to SIGNAL Terminated ***
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ ls -t "$RX_ROOT"/E11/logs/*.log | head -4 | while read f; do echo "== $f"; tail -n 3 "$f"; done
== /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E11/logs/simulate.21774383_0.log
SIM_C_U seed 17 round 004: train=0.269914 val_context_macro=0.600061
SIM_C_U seed 17 round 005: train=0.257485 val_context_macro=0.596966
SIM_C_U seed 17 round 006: train=0.249248 val_context_macro=0.593247
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ sacct -X -u "$USER" -S now-2days -s F,TO,OOM,NF -o JobID%20,JobName%24,State,Elapsed,ExitCode
               JobID                  JobName      State    Elapsed ExitCode
-------------------- ------------------------ ---------- ---------- --------
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cat "$RX_ROOT/E06/results/report.md"
cat: /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E06/results/report.md: No such file or directory
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
