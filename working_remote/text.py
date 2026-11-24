https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


(base) 4475918@hpctpa3pl0001:~$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21774366  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774365  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774359  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774358  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
21774364_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774357_[0-447%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
       21774363_84  red rx_E08B_algo  4475918  R       6:28 1-23:53:32   1   8 gres/gpu:  64G hpctpa3pc0029
       21774356_58  red rx_E08_parti  4475918  R       6:28 1-23:53:32   1   8 gres/gpu:  64G hpctpa3pc0047
(base) 4475918@hpctpa3pl0001:~$ sacct -j 21774351 \
>   -o JobID%22,JobName%36,State%24,ExitCode,Elapsed,Timelimit,ReqMem,MaxRSS
logs=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_2                 JobID                              JobName                    State ExitCode    Elapsed  Timelimit     ReqMem     MaxRSS
---------------------- ------------------------------------ ------------------------ -------- ---------- ---------- ---------- ----------
              21774351             rx_E07_exposure-finalize                   FAILED      1:0   00:02:54 2-00:00:00       128G
        21774351.batch                                batch                   FAILED      1:0   00:02:54                          977360K
       21774351.extern                               extern                COMPLETED      0:0   00:02:54                
(base) 4475918@hpctpa3pl0001:~$
(base) 4475918@hpctpa3pl0001:~$ logs=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs
(base) 4475918@hpctpa3pl0001:~$ tail -n 100 "$logs/exposure-finalize.21774351.log"
rx stage E07/exposure-finalize on hpctpa3pc0030 job 21774351 python /home/4475918/.conda/envs/compass-foundation-test/bin/python
Validated bootstrap study 1/8
Validated bootstrap study 2/8
Validated bootstrap study 3/8
Validated bootstrap study 4/8
Validated bootstrap study 5/8
Validated bootstrap study 6/8
Validated bootstrap study 7/8
Validated bootstrap study 8/8
Traceback (most recent call last):
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rx.py", line 76, in <module>
    raise SystemExit(main())
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rx.py", line 64, in main
    orchestrate.run_stage(args.experiment, args.stage, args.array_index)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/orchestrate.py", line 279, in run_stage
    module(ctx.experiment).run(ctx, stage, array_index)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/experiments/e07_tumor_exposure.py", line 117, in run
    _shared.trained_run(ctx, stage, index, panel=PANEL, contrasts=contrasts(ctx), analyze=analyze)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/experiments/_shared.py", line 225, in trained_run
    run_clinical_stage(ctx, name, step, index, models_tsv=ctx.path("foundation/models.tsv"), contrasts=clinical_contrasts(own))
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/experiments/_shared.py", line 66, in run_clinical_stage
    clinical.finalize(dirs["manifest"], dirs["launch"], dirs["finalized"], replicates=int(ctx.config["bootstrap_replicates"]),
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/rexp/clinical.py", line 300, in finalize
    return finalizer.finalize(package_manifest, output_dir, replicates, seed, None, published)
  File "/share/lab_goecks/paulo/federated-learning-model/HPC_analysis_new/scripts/finalize_experiment.py", line 719, in finalize
    effects = factorial.planned_contrast_rows(evidence["metrics"], config)
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_test/scripts/11_analyze_factorial_and_seed_effects.py", line 315, in planned_contrast_rows
    raise ValueError(f"Required contrast {contrast['contrast_id']} missing arms {sorted(missing)} at {key}")
ValueError: Required contrast normal_tissue_MIX_CEN_minus_TONLY_X025 missing arms ['MIX_CEN_X025', 'TONLY_X025'] at ('reviewer_E07', '24', '7', 'NA', 'nested_grouped_auprc', 'LFT', 'whole_cohort', 'NA', 24, 'Choueiri')
(base) 4475918@hpctpa3pl0001:~$
