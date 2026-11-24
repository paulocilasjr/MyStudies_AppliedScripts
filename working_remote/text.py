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
       21774356_58  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (user env retrieval failed requeued held)
       21774363_84  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (user env retrieval failed requeued held)
(base) 4475918@hpctpa3pl0001:~$ ^C
(base) 4475918@hpctpa3pl0001:~$ ^C
(base) 4475918@hpctpa3pl0001:~$ scontrol release 21774356_58
(base) 4475918@hpctpa3pl0001:~$ scontrol release 21774363_84
(base) 4475918@hpctpa3pl0001:~$ squeue -u "$USER" -o '%.24i %.36j %.12T %R %E'

                   JOBID                                 NAME        STATE NODELIST(REASON) DEPENDENCY
(base) 4475918@hpctpa3pl0001:~$
(base) 4475918@hpctpa3pl0001:~$ sacct -D -X -j 21774356_58,21774363_84 \
>   -o JobID%22,State%24,ExitCode,NodeList%24,End
                 JobID                    State ExitCode                 NodeList                 End
---------------------- ------------------------ -------- ------------------------ -------------------
           21774356_58                 REQUEUED      0:0            hpctpa3pc0030 2026-11-12T04:45:20
           21774363_84                 REQUEUED      0:0            hpctpa3pc0028 2026-11-11T17:49:41
           21774363_84                  RUNNING      0:0            hpctpa3pc0029             Unknown
           21774356_58                  RUNNING      0:0            hpctpa3pc0047             Unknown
(base) 4475918@hpctpa3pl0001:~$
(base) 4475918@hpctpa3pl0001:~$ scontrol show job 21774352
JobId=21774352 JobName=rx_E07_analyze
   UserId=4475918(87748) GroupId=g_4475918(87748) MCS_label=N/A
   Priority=11516 Nice=0 Account=paulocilas.moraislyra QOS=medium WCKey=*4475918
   JobState=PENDING Reason=DependencyNeverSatisfied Dependency=afterok:21774351(failed)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:00:00 TimeLimit=2-00:00:00 TimeMin=N/A
   SubmitTime=2026-11-06T07:19:59 EligibleTime=Unknown
   AccrueTime=Unknown
   StartTime=Unknown EndTime=Unknown Deadline=N/A
   SuspendTime=None SecsPreSuspend=0 LastSchedEval=2026-11-06T07:19:59 Scheduler=Main
   Partition=red AllocNode:Sid=hpctpa3pl0002:3757656
   ReqNodeList=(null) ExcNodeList=(null)
   NodeList=
   NumNodes=1 NumCPUs=16 NumTasks=1 CPUs/Task=16 ReqB:S:C:T=0:0:*:*
   ReqTRES=cpu=16,mem=128G,node=1,billing=16
   AllocTRES=(null)
   Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
   MinCPUsNode=16 MinMemoryNode=128G MinTmpDiskNode=0
   Features=(null) DelayBoot=00:00:00
   OverSubscribe=OK Contiguous=0 Licenses=(null) LicensesAlloc=(null) Network=(null)
   Command=/share/lab_goecks/paulo/federated-learning-model/HPC_reviewer_experiments/slurm/rx_job.sbatch
   WorkDir=/share/lab_goecks/paulo/federated-learning-model
   StdErr=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/analyze.21774352.log
   StdIn=/dev/null
   StdOut=/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E07/logs/analyze.21774352.log
   TresPerTask=cpu=16


(base) 4475918@hpctpa3pl0001:~$ sacct -X -j PARENT_ID -o JobID,JobName%36,State%24,ExitCode,Elapsed
sacct: fatal: Bad job/step specified: PARENT_ID
(base) 4475918@hpctpa3pl0001:~$
(base) 4475918@hpctpa3pl0001:~$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          21774366  red rx_E08B_anal  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774365  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774359  red rx_E08_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774358  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
          21774352  red rx_E07_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (DependencyNeverSatisfied)
21774364_[0-399%8]  red rx_E08B_algo  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
21774357_[0-447%8]  red rx_E08_parti  4475918 PD       0:00 2-00:00:00   1   8 gres/gpu:  64G (Dependency)
       21774363_84  red rx_E08B_algo  4475918  R       1:02 1-23:58:58   1   8 gres/gpu:  64G hpctpa3pc0029
       21774356_58  red rx_E08_parti  4475918  R       1:02 1-23:58:58   1   8 gres/gpu:  64G hpctpa3pc0047
(base) 4475918@hpctpa3pl0001:~$
