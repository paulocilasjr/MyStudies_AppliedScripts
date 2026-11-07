Agents as Virtual Users: Improving How AI Agents Use Galaxy for Cancer Data Analysis

Paulo Cilas Morais Lyra Jr., Junhao Qiu, Alyssa F. Pybus, Isis Narvaez-Bandera, Jeremy Goecks

H. Lee Moffitt Cancer Center & Research Institute, Tampa, FL

Purpose:
Cancer researchers are increasingly using AI agents such as ChatGPT Codex to perform data analyses, from multi-omic profiling to single-cell analysis and even machine learning. However, analyses by agents alone are often difficult to understand and reproduce because agents generate a large amount of code. To address this limitation, we made AI agents virtual users of Galaxy, a computational biomedical workbench built for accessible, reproducible, and scalable analysis. We benchmarked agents in Galaxy, then found and fixed interface problems.

Methods:
We evaluated the ability of AI agents to accurately perform data analysis tasks using either Galaxy or their own code. We used four large language models—GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Pro—in a common Codex agent harness. The 160 tasks came from three sources: (1) Intergalactic Workflow Commission (IWC; 10 tasks), (2) BixBench-Verified-50 (50 tasks), and (3) CompBioBench (100 tasks). Each model, task, and condition was run in triplicate, yielding 3,840 primary runs. Three models also ran 10 harder multi-step IWC analyses (180 runs). We compared run outcomes and measured token use across interface versions.

Results:
Agents using Galaxy matched or exceeded the accuracy of agents writing their own code, scoring higher in 12 of 15 model-benchmark comparisons: 99.0% versus 95.3% on IWC, 89.5% versus 88.3% on BixBench, and 87.0% versus 86.8% on CompBioBench. On multi-step IWC analyses the gap was 67.5% versus 58.7% (references built in Galaxy). The largest gap was in multiplex tissue imaging, used to map tumor microenvironments: 86% versus 9% of results passed, and 6 of 9 Galaxy runs but no custom-code run got every result right. Galaxy supplied the full imaging toolchain; custom-code agents substituted other methods, partly because packages failed to install. Galaxy was also more consistent: every IWC Galaxy run scored at least 87%; 4 custom-code runs scored 0. Every Galaxy run left an inspectable history of the datasets, tools, and parameters behind its answer. Galaxy's main cost was token use, 1.0- to 4.1-fold that of custom code. The MCP server used in these runs, which submits jobs, waits, and returns compact results, had already cut GPT-5.5 tokens 55% on BixBench. Later changes—capped replies, parameter templates, tool checks, and longer job waits—cut GPT-5.6 Sol tokens 56% more, from 3.4- to 1.5-fold, with similar accuracy (137 versus 136 of 150).

Conclusion:
AI agents can perform diverse cancer and biomedical data analyses in Galaxy with accuracy comparable to writing their own code, at a token cost that interface design can reduce. By using Galaxy, agents create analysis histories that are inspectable, reproducible, reusable, and scalable. These histories enable cancer researchers to easily understand, reproduce, and scale agent-based work.

Claude Opus 5.5 helped write this abstract; the authors verified all statements.
