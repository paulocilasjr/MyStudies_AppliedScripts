https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 --from-stage exposure-finalize --allow-code-change && scancel 21774352
-o JobID,JobName%36,State%24,ExitCode/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/submission_20261125T012441+0000.json
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457354  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          22457353  red rx_E07_expos  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Priority)
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ sacct -X -j 21774358,21774359,21774365,21774366 -o JobID,JobName%36,State%24,ExitCode
JobID                                     JobName                    State ExitCode
------------ ------------------------------------ ------------------------ --------
21774358               rx_E08_partitions-finalize                COMPLETED      0:0
21774359                           rx_E08_analyze                COMPLETED      0:0
21774365              rx_E08B_algorithms-finalize                COMPLETED      0:0
21774366                          rx_E08B_analyze                COMPLETED      0:0
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$
