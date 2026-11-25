https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ sacct -X -j 22457353,22457354 -o JobID,JobName%36,State%24,ExitCode,Elapsed
JobID                                     JobName                    State ExitCode    Elapsed
------------ ------------------------------------ ------------------------ -------- ----------
22457353                 rx_E07_exposure-finalize                  RUNNING      0:0   00:01:39
22457354                           rx_E07_analyze                  PENDING      0:0   00:00:00
d"(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ less "$RX_ROOT/E07/results/report.md"
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/results/report.md: No such file or directory
(base) 4475918@hpctpa3pl0001:rx-e07.51U39u(main)$ paulo
(base) 4475918@hpctpa3pl0001:paulo$ cd federated-learning-model/
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ less "$RX_ROOT/E07/results/report.md"
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/results/report.md: No such file or directory
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457354  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          22457353  red rx_E07_expos  4475918  R       2:03 1-23:57:57   1  16       N/A 128G hpctpa3pc0054
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
