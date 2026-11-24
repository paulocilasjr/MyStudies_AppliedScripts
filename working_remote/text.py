https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


scontrol release 21774356_58
scontrol release 21774363_84
squeue -u "$USER" -o '%.24i %.36j %.12T %R %E'


sacct -D -X -j 21774356_58,21774363_84 \
  -o JobID%22,State%24,ExitCode,NodeList%24,End

scontrol show job 21774352
sacct -X -j PARENT_ID -o JobID,JobName%36,State%24,ExitCode,Elapsed

bash HPC_reviewer_experiments/submit/E07_tumor_exposure.sh \
  --from-stage exposure-finalize --dry-run

scancel 21774352
bash HPC_reviewer_experiments/submit/E07_tumor_exposure.sh \
  --from-stage exposure-finalize
