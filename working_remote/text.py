(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
ad -1)"(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -n 2 "$(ls -t "$RX_ROOT"/E0embeddings.*.log | head -1)"
    raise ValueError("Object arrays cannot be loaded when "
ValueError: Object arrays cannot be loaded when allow_pickle=False
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ set -a; source hpc/site.env; set +a
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ tail -n 2 "$(ls -t "$RX_ROOT"/E03/logs/embeddings.*.log | head -1)"
    raise ValueError("Object arrays cannot be loaded when "
ValueError: Object arrays cannot be loaded when allow_pickle=False
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git pull --ff-only
remote: Enumerating objects: 18, done.
remote: Counting objects: 100% (18/18), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 10 (delta 8), reused 10 (delta 8), pack-reused 0 (from 0)
Unpacking objects: 100% (10/10), 3.14 KiB | 32.00 KiB/s, done.
From github.com:paulocilasjr/federated-learning-model
   fda6385..70bf28d  main       -> origin/main
Updating fda6385..70bf28d
Fast-forward
 HPC_reviewer_experiments/rexp/experiments/e03_seed_ensembling.py |  6 ++-
 HPC_reviewer_experiments/rexp/experiments/e11_hpc_deployment.py  | 15 ++++--
 .../rexp/experiments/e13_broader_validation.py                   |  2 +-
 HPC_reviewer_experiments/tests/test_experiment_stages.py         | 85 ++++++++++++++++++++++++++++++
 4 files changed, 100 insertions(+), 8 deletions(-)
 create mode 100644 HPC_reviewer_experiments/tests/test_experiment_stages.py
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ git log -1 --oneline
70bf28d (HEAD -> main, origin/main, origin/HEAD) e13,  e11, e03 bug fixes
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ bash HPC_reviewer_experiments/submit/E03_seed_ensembling.sh --only embeddings --allow-code-change
predictions                  job          cpu_large      after=-  probability/rank ensembles with paired bootstrap
embed                        array[16]    embed_gpu      after=-  frozen concept embeddings of the clinical cohorts
embeddings                   job          cpu_large      after=predictions,embed  nested LOCO logistic probes on single vs ensembled embeddings; report
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E03/submission_20261106T125328+0000.json
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
 21774339_[4-14%4]  red rx_E06_train  4475918 PD       0:00 3-00:00:00   1   8 gres/gpu:  64G (JobArrayTaskLimit)
        21774381_1  red compass_fl_c  4475918 PD       0:00 7-00:00:00   1   8 gres/gpu:  64G (Priority)
          21774465  red rx_E03_embed  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Priority)
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
        21774383_0  red rx_E11_simul  4475918  R       8:57 2-23:51:03   1   8 gres/gpu:  64G hpctpa3pc0008
        21774381_0  red compass_fl_c  4475918  R       8:55 6-23:51:05   1   8 gres/gpu:  64G hpctpa3pc0066
        21774339_3  red rx_E06_train  4475918  R      20:03 2-23:39:57   1   8 gres/gpu:  64G hpctpa3pc0001
        21774339_2  red rx_E06_train  4475918  R      22:37 2-23:37:23   1   8 gres/gpu:  64G hpctpa3pc0051
        21774339_1  red rx_E06_train  4475918  R      24:42 2-23:35:18   1   8 gres/gpu:  64G hpctpa3pc0039
        21774339_0  red rx_E06_train  4475918  R      25:37 2-23:34:23   1   8 gres/gpu:  64G hpctpa3pc0030
          21774380  red compass_fl_s  4475918  R      32:11 6-23:27:49   1   2       N/A  16G hpctpa3pc0024
        21774346_1  red rx_E07_train  4475918  R      17:10 2-23:42:50   1   8 gres/gpu:  64G hpctpa3pc0068
        21774346_0  red rx_E07_train  4475918  R      19:53 2-23:40:07   1   8 gres/gpu:  64G hpctpa3pc0055
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ squeue -u "$USER" -n compass_fl_srv,compass_fl_cli -o "%.18i %.12j %.3t %R"
             JOBID         NAME  ST NODELIST(REASON)
        21774381_1 compass_fl_c  PD (Priority)
        21774381_0 compass_fl_c   R hpctpa3pc0066
          21774380 compass_fl_s   R hpctpa3pc0024
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ for e in E03 E10; do echo "== $e"; "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status $e; done
== E03
T/E03/results/report.md"
cat "$RX_ROOT/E10/results/report.md"  predictions                  complete 1/1  failed 0  running 0
embed                        complete 16/16  failed 0  running 0
embeddings                   complete 0/1  failed 1  running 0
== E10
embed                        complete 16/16  failed 0  running 0
attribution                  complete 16/16  failed 0  running 0
analyze                      complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cat "$RX_ROOT/E03/results/report.md"
cat: /share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E03/results/report.md: No such file or directory
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$ cat "$RX_ROOT/E10/results/report.md"
# E10: Federated vs centralized: representation similarity and immune concepts driving response

Generated 2026-11-06T12:46:15+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

## Representation similarity (linear CKA; bootstrap over samples)

| subset | view | pair_type | mean_linear_cka | ci95_low | ci95_high |
|---|---|---|---|---|---|
| icb_patients | concepts44 | [B_U~C_U:different_seed] - [B_U~B_U] | -0.1289 | -0.1457 | -0.1121 |
| icb_patients | concepts44 | [B_U~C_U:same_seed] - [B_U~B_U] | -0.0355 | -0.0551 | -0.0133 |
| icb_patients | concepts44 | [C_U~C_U] - [B_U~B_U] | -0.1104 | -0.1319 | -0.0885 |
| icb_patients | geneset133 | [B_U~C_U:different_seed] - [B_U~B_U] | -0.0530 | -0.0671 | -0.0415 |
| icb_patients | geneset133 | [B_U~C_U:same_seed] - [B_U~B_U] | 0.0373 | 0.0203 | 0.0493 |
| icb_patients | geneset133 | [C_U~C_U] - [B_U~B_U] | -0.0032 | -0.0284 | 0.0184 |
| probe_tcga | concepts44 | [B_U~C_U:different_seed] - [B_U~B_U] | -0.1003 | -0.1241 | -0.0770 |
| probe_tcga | concepts44 | [B_U~C_U:same_seed] - [B_U~B_U] | 0.0144 | -0.0222 | 0.0430 |
| probe_tcga | concepts44 | [C_U~C_U] - [B_U~B_U] | -0.0306 | -0.0483 | -0.0107 |
| probe_tcga | geneset133 | [B_U~C_U:different_seed] - [B_U~B_U] | -0.0267 | -0.0356 | -0.0177 |
| probe_tcga | geneset133 | [B_U~C_U:same_seed] - [B_U~B_U] | 0.0457 | 0.0334 | 0.0559 |
| probe_tcga | geneset133 | [C_U~C_U] - [B_U~B_U] | 0.0350 | 0.0202 | 0.0450 |

A difference near zero means a federated encoder is as similar to a centralized one as two centralized seeds are to each other.

## Concept attribution agreement (mean |SHAP| over held-out patients)

| pair_type | pairs | mean_spearman_importance | mean_top10_jaccard |
|---|---|---|---|
| A_U~A_U | 10 | 0.5417 | 0.3132 |
| A_U~B_U:different_seed | 20 | 0.4745 | 0.2250 |
| A_U~B_U:same_seed | 5 | 0.5659 | 0.2853 |
| A_U~C_U:different_seed | 20 | 0.4007 | 0.2127 |
| A_U~C_U:same_seed | 5 | 0.5015 | 0.2206 |
| A_U~R:different_seed | 5 | -0.0478 | 0.0433 |
| B_U~B_U | 10 | 0.5341 | 0.2504 |
| B_U~C_U:different_seed | 20 | 0.4702 | 0.2167 |
| B_U~C_U:same_seed | 5 | 0.5731 | 0.2111 |
| B_U~R:different_seed | 5 | 0.0755 | 0.1022 |
| C_U~C_U | 10 | 0.4950 | 0.2650 |
| C_U~R:different_seed | 5 | 0.1502 | 0.1634 |

## Top concepts per family

| family | immune_share | top_concepts |
|---|---|---|
| A_U | 0.3738 | Genome_integrity; CD8_Tcell; Apoptosis_pathway; Cell_proliferation; Innate_lymphoid_cell; Tcell_general; cDC; Fibroblast; Cytotoxic_Tcell; Macrophage |
| B_U | 0.3806 | CD8_Tcell; cDC; Genome_integrity; Cell_proliferation; Macrophage; Treg; Stroma; Plasma_cell; Reference; Cytotoxic_Tcell |
| C_U | 0.3312 | Epithelial; Cell_proliferation; Genome_integrity; Reference; Cytotoxic_Tcell; Macrophage; cDC; Fibroblast; Apoptosis_pathway; IFNg_pathway |
| R | 0.3621 | CANCER; Mast; CD4_Tcell; Epithelial; Erythrocyte; Exhausted_Tcell; IFNg_pathway; cDC; pDC; Naive_Tcell |

Refit reproduction against stored predictions is in attribution_by_model.tsv. Attributions explain the refitted LFT heads on the frozen concept layer; they describe what each model uses, not causal biology. Immune concepts are flagged by keyword (config) and the complete concept list is exported for expert review.
(base) 4475918@hpctpa3pl0002:federated-learning-model(main *)$
