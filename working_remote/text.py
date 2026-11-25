https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


"$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 --from-stage exposure-finalize --allow-code-change && scancel 21774352
qstat

sacct -X -j 21774358,21774359,21774365,21774366 -o JobID,JobName%36,State%24,ExitCode
