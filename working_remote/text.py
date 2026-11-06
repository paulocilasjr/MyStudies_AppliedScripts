(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -n rx_E07_train,rx_E08_train,rx_E08B_train,rx_E12_train -o %A | sort -u | xargs -r scontrol release
21774346_1: Job has already finished
21774346_2-37: No error
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ scontrol update JobId=21774339 ArrayTaskThrottle=8
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -t R -o "%.18i %.24j %.11M %R"
             JOBID                     NAME        TIME NODELIST(REASON)
        21774383_0          rx_E11_simulate     1:20:53 hpctpa3pc0008
        21774381_0           compass_fl_cli     1:20:51 hpctpa3pc0066
          21774380           compass_fl_srv     1:44:07 hpctpa3pc0024
        21774339_3             rx_E06_train     1:31:59 hpctpa3pc0001
        21774339_2             rx_E06_train     1:34:33 hpctpa3pc0051
        21774339_1             rx_E06_train     1:36:38 hpctpa3pc0039
        21774339_0             rx_E06_train     1:37:33 hpctpa3pc0030
        21774381_1           compass_fl_cli        6:26 hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21774339_[4-14%8]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Resources)
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
 21774367_[0-17%4]  red rx_E12_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774360_[0-23%4]  red rx_E08B_trai  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774353_[0-26%4]  red rx_E08_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
 21774346_[2-37%4]  red rx_E07_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (Priority)
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
        21774383_0  red rx_E11_simul  4475918  R    1:20:56 2-22:39:04   1   8 gres/gpu:  64G hpctpa3pc0008
        21774381_0  red compass_fl_c  4475918  R    1:20:54 6-22:39:06   1   8 gres/gpu:  64G hpctpa3pc0066
          21774380  red compass_fl_s  4475918  R    1:44:10 6-22:15:50   1   2       N/A  16G hpctpa3pc0024
        21774339_3  red rx_E06_train  4475918  R    1:32:02 2-22:27:58   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R    1:34:36 2-22:25:24   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R    1:36:41 2-22:23:19   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R    1:37:36 2-22:22:24   1   8 gres/gpu:  64G hpctpa3pc0030
        21774381_1  red compass_fl_c  4475918  R       6:29 6-23:53:31   1   8 gres/gpu:  64G hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
