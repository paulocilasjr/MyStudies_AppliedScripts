Making AI Agent Cancer Data Analyses Understandable, Reproducible, and Scalable 

Paulo Lyra, Jr.1, Junhao Qiu1, Alyssa Pybus1, Isis Narvaez-Bandera1, Jeremy Goecks1 

1Department of Machine Learning, H. Lee Moffitt Cancer Center and Research Institute, Tampa, FL, USA 

Background 

Cancer researchers are increasingly using AI agents such as ChatGPT Codex to perform data analyses, from multi-omic profiling to single-cell analysis and even machine learning. However, using AI agents for cancer data analyses presents two key challenges. First, analyses performed by an agent are often difficult to understand and reproduce as the agent generates a large amount of code. Second, the agent's large-scale analysis performance is limited by the researcher’s computer. To address these limitations, we have integrated AI agents with the Galaxy computational workbench. Galaxy is a computational biomedical workbench built for accessible, reproducible, and scalable analysis. To evaluate agent integration with Galaxy, we have benchmarked agent performance on cancer and biomedical data analyses using Galaxy. 

Methods 

We evaluated the ability of AI agents to accurately perform data analysis tasks using either Galaxy or their own code. We used four different large language models—GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Pro—in a common Codex agent harness. The 160 tasks were obtained from three benchmarks: (1) WorkflowBench (10 tasks), (2) BixBench-Verified-50 (50 tasks), and CompBioBench (100 tasks). Each model, task, and condition was run in triplicate, yielding 3,840 primary runs. 

Results 

Agents using Galaxy to answer these biomedical data analysis tasks matched or exceeded the accuracy of agents writing their own code: 98.2% versus 94.6% accuracy on IWC, 87.7% versus 87.2% accuracy on BixBench, and 87.0% versus 86.7% on CompBioBench. By using Galaxy, agents were able to leverage Galaxy’s user interface to clearly show how analyses were performed and ensure they were reproducible. For tasks with large datasets or computing requirements, agents were able to use Galaxy’s high-performance computing infrastructure. Using Galaxy resulted in higher analysis costs. Median cost per task was 1.9–3.5-fold higher with Galaxy.  

Conclusion 

AI agents can perform diverse cancer and biomedical data analyses in Galaxy with accuracy comparable to writing their own code though at a higher cost. By using Galaxy, agents create analysis histories that are inspectable, reproducible, reusable, and scalable. These analysis histories enable cancer researchers to easily understand, reproduce, and scale agent-based work and create high-quality data analyses. 
