(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21774367_[0-17%4]  red rx_E12_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774360_[0-23%4]  red rx_E08B_trai  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774353_[0-26%4]  red rx_E08_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774346_[2-37%4]  red rx_E07_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Resources)
 21774339_[4-14%4]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
    21774381_[0-1]  red compass_fl_c  4475918 PD       0:00 7-00:00:00   1   8 gres/gpu:  64G (Priority)
    21774383_[0%4]  red rx_E11_simul  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
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
       21774259_15  red rx_E10_attri  4475918  R      13:21 1-23:46:39   1   8 gres/gpu:  64G hpctpa3pc0066
        21774346_1  red rx_E07_train  4475918  R       2:55 2-23:57:05   1   8 gres/gpu:  64G hpctpa3pc0068
        21774346_0  red rx_E07_train  4475918  R       5:38 2-23:54:22   1   8 gres/gpu:  64G hpctpa3pc0055
        21774339_3  red rx_E06_train  4475918  R       5:48 2-23:54:12   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R       8:22 2-23:51:38   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R      10:27 2-23:49:33   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R      11:22 2-23:48:38   1   8 gres/gpu:  64G hpctpa3pc0030
          21774380  red compass_fl_s  4475918  R      17:56 6-23:42:04   1   2       N/A  16G hpctpa3pc0024
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cd /share/lab_goecks/paulo/federated-learning-model
 --ff-only
git log -1 --oneline
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git pull --ff-only
remote: Enumerating objects: 11, done.
remote: Counting objects: 100% (11/11), done.
remote: Compressing objects: 100% (1/1), done.
remote: Total 6 (delta 5), reused 6 (delta 5), pack-reused 0 (from 0)
Unpacking objects: 100% (6/6), 968 bytes | 17.00 KiB/s, done.
From github.com:paulocilasjr/federated-learning-model
   e73c6d5..fda6385  main       -> origin/main
Updating e73c6d5..fda6385
Fast-forward
 HPC_reviewer_experiments/rexp/experiments/e11_hpc_deployment.py | 22 ++++++++++++++++------
 1 file changed, 16 insertions(+), 6 deletions(-)
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git log -1 --oneline
fda6385 (HEAD -> main, origin/main, origin/HEAD) e11 hpc fix
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol hold
s cluster; the hold is enough"

squeue -u "$USER" -n compass_fl_srv,compass_fl_cli -o "%.18i %.12j %.3t %R"
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ scontrol top 21774381 2>/dev/null || echo "scontrol top not enabled on this cluster; the hold is enough"
scontrol top not enabled on this cluster; the hold is enough
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -n compass_fl_srv,compass_fl_cli -o "%.18i %.12j %.3t %R"
             JOBID         NAME  ST NODELIST(REASON)
    21774381_[0-1] compass_fl_c  PD (Resources)
          21774380 compass_fl_s   R hpctpa3pc0024
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -5 /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_analysis_new/launch_fix_20261019T014157Z/federated_project/logs/server.21774380.log
INFO :      [INIT]
INFO :      Using initial global parameters provided by strategy
INFO :      Evaluating initial global parameters
INFO :
INFO :      [ROUND 1]
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for e in E03 E06 E10 E11; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
== E03
predictions                  complete 1/1  failed 0  running 0
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 0/1  failed 1  running 0
== E06
train                        complete 0/15  failed 0  running 4
collect                      complete 0/1  failed 0  running 0
recipe-plan                  complete 0/1  failed 0  running 0
recipe-owners                complete 0/128  failed 0  running 0
recipe-remaining             complete 0/256  failed 0  running 0
recipe-finalize              complete 0/1  failed 0  running 0
analyze                      complete 0/1  failed 0  running 0
== E10
embed                        complete 16/16  failed 0  running 0
attribution                  complete 15/16  failed 0  running 1
analyze                      complete 0/1  failed 0  running 0
== E11
deploy                       complete 0/1  failed 0  running 0
simulate                     complete 0/1  failed 0  running 0
benchmark                    complete 0/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
