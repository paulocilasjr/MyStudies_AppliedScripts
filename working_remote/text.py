AI agents analyzing biomedical data in Galaxy match code-writing agents in accuracy and leave reproducible records

Paulo Lyra, Jr.¹, Junhao Qiu¹, Alyssa Pybus¹, Isis Narvaez-Bandera¹, Jeremy Goecks¹
¹Department of Machine Learning, H. Lee Moffitt Cancer Center and Research Institute, Tampa, FL, USA

Background
Artificial intelligence (AI) agents can run multi-omic and single-cell analyses for cancer researchers, but they write ad hoc code on the researcher's computer that is hard to inspect, reproduce or scale. Galaxy, an open workbench, records every tool, parameter and dataset and runs jobs on shared computing infrastructure. We asked whether agents working in Galaxy are as accurate as agents writing their own code, and used agents as virtual users to find what limits them.

Methods
Four large language models (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, DeepSeek V4 Pro) in the Codex harness performed 160 tasks from BixBench-Verified-50, CompBioBench and Intergalactic Workflow Commission (IWC) workflows, including tumor-versus-normal proteomics, lung tumor single-cell RNA-seq and CRISPR screen analyses. Each task ran in triplicate in Galaxy, with installed or agent-written user-defined tools (UDTs), and with custom code (3,840 runs). We report paired differences with 95% cluster bootstrap intervals, failure causes and token use. Codex (GPT-6) and Claude Code (Claude Opus 5.5) assisted result analysis.

Results
Galaxy accuracy was similar to custom code on BixBench (89.5% vs 88.3%; difference 1.2 points, 95% interval −1.5 to 4.2) and CompBioBench (official score 87.0 vs 86.8) and higher on IWC (99.0% vs 95.3% output agreement; 0.8 to 7.3), mostly in three workflows. All 1,920 Galaxy runs left a usegalaxy.org history linking each answer to its tools, parameters and data. UDTs appeared in 39% of BixBench and 70% of CompBioBench Galaxy runs, yet installed tools alone solved 42 of 50 BixBench tasks in an earlier campaign. Run records showed agents accessing earlier answers, traces or references in 71 runs; replacing these and 6 other flagged runs reversed no comparison. Galaxy rarely caused errors: of 133 incorrect BixBench runs (63 Galaxy, 70 custom code), most were task-specification (77) or missing-validation (31) errors in both conditions; only 6 were attributed to Galaxy or the harness. The cost was tokens: Galaxy used 4.1-, 2.5- and 1.0-fold the tokens of custom code on BixBench, CompBioBench and IWC. In one traced batch, Galaxy agents took 2.66 times as many turns, each carrying 2.20 times the context. Compact tool replies and longer job waits cut Galaxy use by 56%, from 122.4 to 54.3 million tokens per 50 BixBench tasks (GPT-5.6 Sol), narrowing the gap to custom code from 3.4- to 1.5-fold with 137 of 150 answers accepted.

Conclusions
AI agents can analyze cancer and biomedical data in Galaxy with accuracy comparable to writing their own code, while leaving histories that researchers can inspect, rerun and reuse. Agents acting as virtual users exposed concrete Galaxy fixes that more than halved token use, a path to auditable, reproducible agent-driven cancer research.

Claude Code (Claude Opus 5.5) helped draft and edit this abstract; the authors verified all statements.
