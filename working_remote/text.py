(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21774339_[4-14%4]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
        21774381_1  red compass_fl_c  4475918 PD       0:00 7-00:00:00   1   8 gres/gpu:  64G (Priority)
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
        21774383_0  red rx_E11_simul  4475918  R      15:51 2-23:44:09   1   8 gres/gpu:  64G hpctpa3pc0008
        21774381_0  red compass_fl_c  4475918  R      15:49 6-23:44:11   1   8 gres/gpu:  64G hpctpa3pc0066
        21774339_3  red rx_E06_train  4475918  R      26:57 2-23:33:03   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R      29:31 2-23:30:29   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R      31:36 2-23:28:24   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R      32:31 2-23:27:29   1   8 gres/gpu:  64G hpctpa3pc0030
          21774380  red compass_fl_s  4475918  R      39:05 6-23:20:55   1   2       N/A  16G hpctpa3pc0024
        21774346_1  red rx_E07_train  4475918  R      24:04 2-23:35:56   1   8 gres/gpu:  64G hpctpa3pc0068
        21774346_0  red rx_E07_train  4475918  R      26:47 2-23:33:13   1   8 gres/gpu:  64G hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next} $h["pair_type"] !~ /^\[/ {printf "%-13s %-10s %-24s %.3f\n",$h["subset"],$h["view"],$h["pair_type"],$h["mean_linear_cka"]}' "$RX_ROOT/E10/results/cka_summary.tsv"
icb_patients  concepts44 A_U~A_U                  0.725
icb_patients  concepts44 A_U~B_U:same_seed        0.700
icb_patients  concepts44 A_U~B_U:different_seed   0.653
icb_patients  concepts44 A_U~C_U:same_seed        0.578
icb_patients  concepts44 A_U~C_U:different_seed   0.534
icb_patients  concepts44 A_U~R:different_seed     0.298
icb_patients  concepts44 B_U~B_U                  0.743
icb_patients  concepts44 B_U~C_U:same_seed        0.707
icb_patients  concepts44 B_U~C_U:different_seed   0.614
icb_patients  concepts44 B_U~R:different_seed     0.303
icb_patients  concepts44 C_U~C_U                  0.632
icb_patients  concepts44 C_U~R:different_seed     0.356
icb_patients  geneset133 A_U~A_U                  0.711
icb_patients  geneset133 A_U~B_U:same_seed        0.811
icb_patients  geneset133 A_U~B_U:different_seed   0.691
icb_patients  geneset133 A_U~C_U:same_seed        0.698
icb_patients  geneset133 A_U~C_U:different_seed   0.610
icb_patients  geneset133 A_U~R:different_seed     0.522
icb_patients  geneset133 B_U~B_U                  0.714
icb_patients  geneset133 B_U~C_U:same_seed        0.751
icb_patients  geneset133 B_U~C_U:different_seed   0.661
icb_patients  geneset133 B_U~R:different_seed     0.554
icb_patients  geneset133 C_U~C_U                  0.710
icb_patients  geneset133 C_U~R:different_seed     0.546
probe_tcga    concepts44 A_U~A_U                  0.574
probe_tcga    concepts44 A_U~B_U:same_seed        0.440
probe_tcga    concepts44 A_U~B_U:different_seed   0.407
probe_tcga    concepts44 A_U~C_U:same_seed        0.261
probe_tcga    concepts44 A_U~C_U:different_seed   0.248
probe_tcga    concepts44 A_U~R:different_seed     0.039
probe_tcga    concepts44 B_U~B_U                  0.657
probe_tcga    concepts44 B_U~C_U:same_seed        0.672
probe_tcga    concepts44 B_U~C_U:different_seed   0.557
probe_tcga    concepts44 B_U~R:different_seed     0.071
probe_tcga    concepts44 C_U~C_U                  0.627
probe_tcga    concepts44 C_U~R:different_seed     0.112
probe_tcga    geneset133 A_U~A_U                  0.603
probe_tcga    geneset133 A_U~B_U:same_seed        0.683
probe_tcga    geneset133 A_U~B_U:different_seed   0.586
probe_tcga    geneset133 A_U~C_U:same_seed        0.562
probe_tcga    geneset133 A_U~C_U:different_seed   0.521
probe_tcga    geneset133 A_U~R:different_seed     0.407
probe_tcga    geneset133 B_U~B_U                  0.587
probe_tcga    geneset133 B_U~C_U:same_seed        0.633
probe_tcga    geneset133 B_U~C_U:different_seed   0.560
probe_tcga    geneset133 B_U~R:different_seed     0.401
probe_tcga    geneset133 C_U~C_U                  0.622
probe_tcga    geneset133 C_U~R:different_seed     0.433
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ column -t -s $'\t' "$RX_ROOT/E10/results/attribution_by_model.tsv"
model             arm  foundation_seed  layer  immune_concepts  immune_share_of_attribution  refits_within_tolerance  refits
a_u_seed17        A_U  17               high   14               0.4314949013007364           24                       24
a_u_seed24        A_U  24               high   14               0.36740874765892045          24                       24
a_u_seed42        A_U  42               high   14               0.34808029180047884          24                       24
a_u_seed64        A_U  64               high   14               0.3477070784939261           24                       24
a_u_seed91        A_U  91               high   14               0.3742702798190898           24                       24
b_u_seed17        B_U  17               high   14               0.403339506568649            24                       24
b_u_seed24        B_U  24               high   14               0.4181010506549913           24                       24
b_u_seed42        B_U  42               high   14               0.4017239867195467           24                       24
b_u_seed64        B_U  64               high   14               0.31577101931294993          24                       24
b_u_seed91        B_U  91               high   14               0.36395876540561845          24                       24
c_u_seed17        C_U  17               high   14               0.39247155006893775          24                       24
c_u_seed24        C_U  24               high   14               0.3585179433353348           24                       24
c_u_seed42        C_U  42               high   14               0.3208197791760365           24                       24
c_u_seed64        C_U  64               high   14               0.24479282039493366          24                       24
c_u_seed91        C_U  91               high   14               0.33929990687429545          24                       24
official_compass  R    NA               high   14               0.36206032335692157          24                       24
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -h -o "%A %j %T %r" | sort -u
21774339 rx_E06_train PENDING JobArrayTaskLimit
21774340 rx_E06_collect PENDING Dependency
21774341 rx_E06_recipe-plan PENDING Dependency
21774342 rx_E06_recipe-owners PENDING Dependency
21774343 rx_E06_recipe-remaining PENDING Dependency
21774344 rx_E06_recipe-finalize PENDING Dependency
21774345 rx_E06_analyze PENDING Dependency
21774346 rx_E07_train PENDING JobHeldUser
21774347 rx_E07_collect PENDING Dependency
21774348 rx_E07_exposure-plan PENDING Dependency
21774349 rx_E07_exposure-owners PENDING Dependency
21774350 rx_E07_exposure-remaining PENDING Dependency
21774351 rx_E07_exposure-finalize PENDING Dependency
21774352 rx_E07_analyze PENDING Dependency
21774353 rx_E08_train PENDING JobHeldUser
21774354 rx_E08_collect PENDING Dependency
21774355 rx_E08_partitions-plan PENDING Dependency
21774356 rx_E08_partitions-owners PENDING Dependency
21774357 rx_E08_partitions-remaining PENDING Dependency
21774358 rx_E08_partitions-finalize PENDING Dependency
21774359 rx_E08_analyze PENDING Dependency
21774360 rx_E08B_train PENDING JobHeldUser
21774361 rx_E08B_collect PENDING Dependency
21774362 rx_E08B_algorithms-plan PENDING Dependency
21774363 rx_E08B_algorithms-owners PENDING Dependency
21774364 rx_E08B_algorithms-remaining PENDING Dependency
21774365 rx_E08B_algorithms-finalize PENDING Dependency
21774366 rx_E08B_analyze PENDING Dependency
21774367 rx_E12_train PENDING JobHeldUser
21774368 rx_E12_collect PENDING Dependency
21774369 rx_E12_attack-mia PENDING Dependency
21774370 rx_E12_attack-inversion PENDING Dependency
21774371 rx_E12_privacy-plan PENDING Dependency
21774372 rx_E12_privacy-owners PENDING Dependency
21774373 rx_E12_privacy-remaining PENDING Dependency
21774374 rx_E12_privacy-finalize PENDING Dependency
21774375 rx_E12_analyze PENDING Dependency
21774380 compass_fl_srv RUNNING None
21774381 compass_fl_cli PENDING Priority
21774382 compass_fl_val PENDING Dependency
21774383 rx_E11_simulate RUNNING None
21774384 rx_E11_benchmark PENDING Dependency
21774447 rx_E06_train RUNNING None
21774448 rx_E06_train RUNNING None
21774453 rx_E06_train RUNNING None
21774454 rx_E06_train RUNNING None
21774455 rx_E07_train RUNNING JobHeldUser
21774462 rx_E07_train RUNNING JobHeldUser
21774463 compass_fl_cli RUNNING None
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
