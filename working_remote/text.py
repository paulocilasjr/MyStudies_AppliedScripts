(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E03
predictions                  complete 1/1  failed 0  running 0
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cat "$RX_ROOT/E03/results/report.md"
# E03: Seed ensembling of pretraining seeds (predictions and embeddings)

Generated 2026-11-06T12:54:17+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

## LFT: prediction ensembles

| family | estimate | bc_ci95_low | bc_ci95_high |
|---|---|---|---|
| A_U | 0.4123 | 0.2830 | 0.5254 |
| A_U_ENS_PROB | 0.4532 | 0.3160 | 0.5907 |
| A_U_ENS_RANK | 0.4445 | 0.3089 | 0.5764 |
| B_U | 0.4001 | 0.2959 | 0.4892 |
| B_U_ENS_PROB | 0.3998 | 0.2751 | 0.5156 |
| B_U_ENS_RANK | 0.3989 | 0.2855 | 0.5118 |
| C_U | 0.3996 | 0.2776 | 0.5056 |
| C_U_ENS_PROB | 0.4113 | 0.2742 | 0.5360 |
| C_U_ENS_RANK | 0.4078 | 0.2662 | 0.5303 |
| R | 0.4574 | 0.3158 | 0.5857 |

| contrast | estimate | q0025 | q0975 | share_of_draws_above_zero |
|---|---|---|---|---|
| A_U_ENS_PROB_minus_mean_single_seed | 0.0410 | -0.0153 | 0.0826 | 0.9048 |
| A_U_ENS_PROB_minus_R | -0.0041 | -0.1263 | 0.0962 | 0.4789 |
| A_U_ENS_RANK_minus_mean_single_seed | 0.0323 | -0.0164 | 0.0732 | 0.8747 |
| A_U_ENS_RANK_minus_R | -0.0128 | -0.1253 | 0.0828 | 0.4349 |
| B_U_ENS_PROB_minus_mean_single_seed | -0.0002 | -0.0433 | 0.0438 | 0.5175 |
| B_U_ENS_PROB_minus_R | -0.0575 | -0.1703 | 0.0572 | 0.1954 |
| B_U_ENS_RANK_minus_mean_single_seed | -0.0012 | -0.0441 | 0.0344 | 0.3946 |
| B_U_ENS_RANK_minus_R | -0.0584 | -0.1725 | 0.0462 | 0.1558 |
| C_U_ENS_PROB_minus_mean_single_seed | 0.0116 | -0.0377 | 0.0653 | 0.6728 |
| C_U_ENS_PROB_minus_R | -0.0461 | -0.1449 | 0.0536 | 0.2043 |
| C_U_ENS_RANK_minus_mean_single_seed | 0.0081 | -0.0278 | 0.0480 | 0.6847 |
| C_U_ENS_RANK_minus_R | -0.0496 | -0.1478 | 0.0504 | 0.1894 |
| federation_under_ensembling_C_U_ENS_minus_B_U_ENS | 0.0114 | -0.0743 | 0.0967 | 0.5915 |
| A_U_ENS_PROB_minus_post_hoc_best_seed_42 | -0.0105 | -0.0955 | 0.0638 |  |
| B_U_ENS_PROB_minus_post_hoc_best_seed_17 | -0.0470 | -0.1518 | 0.0448 |  |
| C_U_ENS_PROB_minus_post_hoc_best_seed_17 | -0.0275 | -0.0836 | 0.0204 |  |

## PFT: prediction ensembles

| family | estimate | bc_ci95_low | bc_ci95_high |
|---|---|---|---|
| A_U | 0.4115 | 0.2869 | 0.5185 |
| A_U_ENS_PROB | 0.4515 | 0.2987 | 0.5799 |
| A_U_ENS_RANK | 0.4373 | 0.2939 | 0.5645 |
| B_U | 0.4008 | 0.2940 | 0.4938 |
| B_U_ENS_PROB | 0.4163 | 0.2814 | 0.5325 |
| B_U_ENS_RANK | 0.4216 | 0.2823 | 0.5414 |
| C_U | 0.4020 | 0.2830 | 0.5029 |
| C_U_ENS_PROB | 0.4052 | 0.2685 | 0.5267 |
| C_U_ENS_RANK | 0.4117 | 0.2716 | 0.5290 |
| R | 0.4434 | 0.2996 | 0.5801 |

| contrast | estimate | q0025 | q0975 | share_of_draws_above_zero |
|---|---|---|---|---|
| A_U_ENS_PROB_minus_mean_single_seed | 0.0400 | -0.0056 | 0.0916 | 0.9614 |
| A_U_ENS_PROB_minus_R | 0.0081 | -0.1119 | 0.1295 | 0.6380 |
| A_U_ENS_RANK_minus_mean_single_seed | 0.0258 | -0.0164 | 0.0705 | 0.8979 |
| A_U_ENS_RANK_minus_R | -0.0061 | -0.1155 | 0.1026 | 0.5538 |
| B_U_ENS_PROB_minus_mean_single_seed | 0.0156 | -0.0310 | 0.0657 | 0.7864 |
| B_U_ENS_PROB_minus_R | -0.0270 | -0.1385 | 0.0899 | 0.4065 |
| B_U_ENS_RANK_minus_mean_single_seed | 0.0208 | -0.0315 | 0.0748 | 0.7798 |
| B_U_ENS_RANK_minus_R | -0.0218 | -0.1447 | 0.1045 | 0.4183 |
| C_U_ENS_PROB_minus_mean_single_seed | 0.0032 | -0.0377 | 0.0526 | 0.6063 |
| C_U_ENS_PROB_minus_R | -0.0382 | -0.1566 | 0.0887 | 0.3389 |
| C_U_ENS_RANK_minus_mean_single_seed | 0.0097 | -0.0281 | 0.0539 | 0.7372 |
| C_U_ENS_RANK_minus_R | -0.0317 | -0.1400 | 0.0851 | 0.3689 |
| federation_under_ensembling_C_U_ENS_minus_B_U_ENS | -0.0111 | -0.0995 | 0.0720 | 0.4037 |
| A_U_ENS_PROB_minus_post_hoc_best_seed_42 | 0.0086 | -0.0508 | 0.0847 |  |
| B_U_ENS_PROB_minus_post_hoc_best_seed_17 | -0.0110 | -0.1166 | 0.0728 |  |
| C_U_ENS_PROB_minus_post_hoc_best_seed_42 | -0.0202 | -0.1109 | 0.0688 |  |

The post-hoc best seed is selected on the same test cohorts and is shown only to bound what seed selection could not legitimately achieve; the ensemble requires no selection.

## Embedding ensembles (nested LOCO logistic probe on frozen concepts)

| family | estimate | bc_ci95_low | bc_ci95_high |
|---|---|---|---|
| A_U | 0.4528 | 0.3178 | 0.5681 |
| A_U_EMB_CONCAT | 0.4518 | 0.2854 | 0.6127 |
| A_U_EMB_MEAN | 0.4341 | 0.2727 | 0.5752 |
| B_U | 0.3840 | 0.2563 | 0.4932 |
| B_U_EMB_CONCAT | 0.4583 | 0.2947 | 0.6097 |
| B_U_EMB_MEAN | 0.3976 | 0.2505 | 0.5419 |
| C_U | 0.4172 | 0.2995 | 0.5273 |
| C_U_EMB_CONCAT | 0.4204 | 0.2741 | 0.5563 |
| C_U_EMB_MEAN | 0.4107 | 0.2564 | 0.5600 |
| R | 0.4700 | 0.2962 | 0.6338 |

| contrast | estimate | q0025 | q0975 |
|---|---|---|---|
| A_U_EMB_MEAN_minus_single_seed_probe | -0.0188 | -0.1349 | 0.1161 |
| A_U_EMB_CONCAT_minus_single_seed_probe | -0.0010 | -0.0683 | 0.0631 |
| A_U_EMB_MEAN_minus_R_probe | -0.0360 | -0.1539 | 0.0818 |
| B_U_EMB_MEAN_minus_single_seed_probe | 0.0136 | -0.0687 | 0.0889 |
| B_U_EMB_CONCAT_minus_single_seed_probe | 0.0743 | -0.0081 | 0.1455 |
| B_U_EMB_MEAN_minus_R_probe | -0.0724 | -0.2272 | 0.0522 |
| C_U_EMB_MEAN_minus_single_seed_probe | -0.0065 | -0.0751 | 0.0910 |
| C_U_EMB_CONCAT_minus_single_seed_probe | 0.0032 | -0.0643 | 0.0695 |
| C_U_EMB_MEAN_minus_R_probe | -0.0594 | -0.2292 | 0.0862 |

Probe families are not comparable to COMPASS fine-tuned heads; compare rows only within this table.
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
        21774383_0  red rx_E11_simul  4475918  R      23:43 2-23:36:17   1   8 gres/gpu:  64G hpctpa3pc0008
        21774381_0  red compass_fl_c  4475918  R      23:41 6-23:36:19   1   8 gres/gpu:  64G hpctpa3pc0066
        21774339_3  red rx_E06_train  4475918  R      34:49 2-23:25:11   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R      37:23 2-23:22:37   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R      39:28 2-23:20:32   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R      40:23 2-23:19:37   1   8 gres/gpu:  64G hpctpa3pc0030
          21774380  red compass_fl_s  4475918  R      46:57 6-23:13:03   1   2       N/A  16G hpctpa3pc0024
        21774346_1  red rx_E07_train  4475918  R      31:56 2-23:28:04   1   8 gres/gpu:  64G hpctpa3pc0068
        21774346_0  red rx_E07_train  4475918  R      34:39 2-23:25:21   1   8 gres/gpu:  64G hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
