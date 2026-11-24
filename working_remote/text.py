https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ git pull
remote: Enumerating objects: 12, done.
remote: Counting objects: 100% (12/12), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 7 (delta 5), reused 7 (delta 5), pack-reused 0 (from 0)
Unpacking objects: 100% (7/7), 9.92 KiB | 143.00 KiB/s, done.
From github.com:paulocilasjr/federated-learning-model
   70bf28d..59ea1d7  main       -> origin/main
Updating 70bf28d..59ea1d7
Fast-forward
 HPC_analysis_new/scripts/finalize_experiment.py    | 18 +++++++++++++++++-
 HPC_analysis_new/tests/test_finalize_experiment.py | 34 ++++++++++++++++++++++++++++------
 2 files changed, 45 insertions(+), 7 deletions(-)
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ repo=/share/lab_goecks/paulo/federated-learning-model
ne --no-local "$repo" "$retry_repo" &&
  git -C "$retry_repo" apply "$HOME/e07-finalize-21774351.patch" &&
  cd "$retry_repo" &&
  "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 \
    --from-stage exposure-finalize --dry-run(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ retry_repo=$(mktemp -d "$HOME/rx-e07.XXXXXX")
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_ROOT="$repo/sources/raw/HPC_reviewer_experiments/run_20261105"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_REPO="$retry_repo"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export RX_PYTHON=/home/4475918/.conda/envs/compass-foundation-test/bin/python
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ git clone --no-local "$repo" "$retry_repo" &&
>   git -C "$retry_repo" apply "$HOME/e07-finalize-21774351.patch" &&
>   cd "$retry_repo" &&
>   "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 \
>     --from-stage exposure-finalize --dry-run
Cloning into '/home/4475918/rx-e07.51U39u'...
remote: Enumerating objects: 2397, done.
remote: Counting objects: 100% (2397/2397), done.
remote: Compressing objects: 100% (1866/1866), done.
remote: Total 2397 (delta 1204), reused 1285 (delta 483), pack-reused 0
Receiving objects: 100% (2397/2397), 31.05 MiB | 44.16 MiB/s, done.
Resolving deltas: 100% (1204/1204), done.
Updating files: 100% (870/870), done.
error: can't open patch '/home/4475918/e07-finalize-21774351.patch': No such file or directory
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
21774357_[30-447%8  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Priority)
21774364_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Priority)
          21774366  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774365  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774359  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774358  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
       21774357_27  red rx_E08_parti  4475918  R       0:15 1-23:59:45   1   8 gres/gpu:  64G hpctpa3pc0029
       21774357_28  red rx_E08_parti  4475918  R       0:15 1-23:59:45   1   8 gres/gpu:  64G hpctpa3pc0047
       21774357_29  red rx_E08_parti  4475918  R       0:15 1-23:59:45   1   8 gres/gpu:  64G hpctpa3pc0035
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$   "$RX_PYTHON" "$RX_REPO/HPC_reviewer_experiments/rx.py" submit E07 \
>   --from-stage exposure-finalize && scancel 21774352
Traceback (most recent call last):
  File "/home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/rx.py", line 76, in <module>
    raise SystemExit(main())
  File "/home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/rx.py", line 59, in main
    receipt = orchestrate.submit(args.experiment, dry_run=args.dry_run, start=args.from_stage, only=args.only,
  File "/home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/rexp/orchestrate.py", line 153, in submit
    require(not changed or allow_code_change,
  File "/home/4475918/rx-e07.51U39u/HPC_reviewer_experiments/rexp/common.py", line 38, in require
    raise RxError(message)
rexp.common.RxError: Reviewer code changed after planning (HPC_reviewer_experiments/rexp/analysis.py, HPC_reviewer_experiments/rexp/orchestrate.py). Plan a new frozen run, or pass --allow-code-change for orchestration-only fixes (recorded in the submission receipt).
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
21774357_[30-447%8  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Priority)
21774364_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Priority)
          21774366  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774365  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774359  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774358  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
       21774357_27  red rx_E08_parti  4475918  R       0:45 1-23:59:15   1   8 gres/gpu:  64G hpctpa3pc0029
       21774357_28  red rx_E08_parti  4475918  R       0:45 1-23:59:15   1   8 gres/gpu:  64G hpctpa3pc0047
       21774357_29  red rx_E08_parti  4475918  R       0:45 1-23:59:15   1   8 gres/gpu:  64G hpctpa3pc0035
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
