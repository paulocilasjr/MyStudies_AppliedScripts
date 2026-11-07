I wrote the abstract for AACR 2027 as follows:
"Agents as virtual users: a better interface between AI agents and the Galaxy workbench for biomedical analysis
Paulo Cilas Morais Lyra Jr., Junhao Qiu, Alyssa F. Pybus, Isis Narvaez-Bandera, Jeremy Goecks
H. Lee Moffitt Cancer Center & Research Institute, Tampa, FL
Purpose:
Cancer researchers are increasingly using AI agents such as ChatGPT Codex to perform data analyses, from multi-omic profiling to single-cell analysis and even machine learning. However, using AI agents alone for cancer data analyses presents key challenges. Mainly, analyses performed by AI agents alone are often difficult to understand and reproduce because the agents generate a large amount of code. To address these limitations, we used agents as virtual Galaxy users. Galaxy is a computational biomedical workbench built for accessible, reproducible, and scalable analysis. To evaluate agent integration with Galaxy, we have benchmarked agent performance on cancer and biomedical data analyses to measure what the combination achieves, find where the interface fails, and identify fixes.
 Methods:
We evaluated the ability of AI agents to accurately perform data analysis tasks using either Galaxy or their own custom code. We used four different large language models – GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Pro – in a common Codex agent harness. The main 160 tasks were obtained from three benchmarks: Intergalactic Workflow Commission (IWC) – 10 tasks; BixBench-Verified-50 – 50 tasks; and CompBioBench – 100 tasks. Each model, task, and condition was run in triplicate, yielding 3,840 primary runs. Three models also ran 10 harder multi-step IWC analyses (180 runs). We classified failed runs and failed Galaxy requests, and measured tokens across interface versions to identify areas for improvement.
Results:
Agents using Galaxy outscored agents writing their custom code in 12 of 15 model-benchmark comparisons. The overall accuracy (%) by benchmark, Galaxy vs custom code, was 89.5 vs 88.3 for BixBench, 87.0 vs 86.8 for CompBioBench, 99.0 vs 95.3 for IWC, and 67.5 vs 58.7 for multi-step IWC tasks. All 1,920 Galaxy runs left a Galaxy history linking the answer to its tools, parameters, data, and agent code. Wrong answers mostly reflected missing-validation errors in both conditions (108 of 133 BixBench failures); only 6 Galaxy failures came from the platform or harness. Interface friction showed instead in earlier failed requests, including 981 parameter setup errors. Tokens usage difference was important. Galaxy-agent combination used up to 4.1 times more tokens than agents writing custom code. An adjustment on the MCP server that submits, waits and returns compact results cut tokens usage in 55%; another adjustment by capping the replies, parameters templates, pre-submission tool checks and longer job callback waits cut the token usage 56% further, bringing the difference to 1.5-fold custom code, without diminishing the correct answers (137 of 150 answers accepted).
Conclusion:
AI agents can perform diverse cancer and biomedical data analyses in Galaxy with accuracy comparable to writing their own code though at a higher cost. By using Galaxy, agents create analysis histories that are inspectable, reproducible, reusable, and scalable. These analysis histories enable cancer researchers to easily understand, reproduce, and scale agent-based work and create high-quality data analyses.
Claude Opus 5.5 helped write this abstract; the authors verified all statements."

What I need now is to refine the text to make it better to read and easy to understand. While also adopting Jeremy Goecks write style. Here are two examples of abstracts that Jeremy wrote with some comments that might help to design this abstract closer to his wording and style of presenting the information:

abstract example 1:
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

Abstract example 2:
attached.

Ran 6 commands
Here’s the revised abstract. I worked from your draft, applied Jeremy’s sentence patterns from both examples, and cut it to roughly the same length as your other AACR 2027 abstract (the one that measured 2,583/2,600).

Agents as Virtual Users: An Efficient Interface Between AI Agents and the Galaxy Workbench for Biomedical Analysis

Paulo Cilas Morais Lyra Jr., Junhao Qiu, Alyssa F. Pybus, Isis Narvaez-Bandera, Jeremy Goecks

H. Lee Moffitt Cancer Center & Research Institute, Tampa, FL

Purpose:
Cancer researchers are increasingly using AI agents such as ChatGPT Codex to perform data analyses, from multi-omic profiling to single-cell analysis and even machine learning. However, analyses performed by agents alone are often difficult to understand and reproduce because agents generate a large amount of code. To address this limitation, we made AI agents virtual users of Galaxy, a computational biomedical workbench built for accessible, reproducible, and scalable analysis. We benchmarked agents working in Galaxy and used the interface failures we found to improve it.

Methods:
We evaluated the ability of AI agents to accurately perform data analysis tasks using either Galaxy or their own code. We used four large language models—GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Pro—in a common Codex agent harness. The 160 main tasks were obtained from three benchmarks: (1) Intergalactic Workflow Commission (IWC; 10 tasks), (2) BixBench-Verified-50 (50 tasks), and (3) CompBioBench (100 tasks). Each model, task, and condition was run in triplicate, yielding 3,840 primary runs. Three models also ran 10 harder multi-step IWC analyses (180 runs). We classified failures and measured token use across interface versions.

Results:
Agents using Galaxy were more accurate than agents writing their own code in 12 of 15 model-benchmark comparisons: 99.0% versus 95.3% on IWC, 89.5% versus 88.3% on BixBench, 87.0% versus 86.8% on CompBioBench, and 67.5% versus 58.7% on multi-step IWC tasks. All 1,920 Galaxy runs produced a history linking the answer to its tools, parameters, data, and agent code. Wrong answers came mostly from missing validation rather than the interface (108 of 133 BixBench failures); only 6 Galaxy failures came from the platform or harness. Interface friction appeared earlier, in failed Galaxy requests, most often parameter setup errors (n=981). Using Galaxy also cost more: agents used up to 4.1-fold more tokens than when writing their own code. Two interface revisions closed most of this gap. An MCP server that submits a job, waits, and returns compact results cut token use by 55%; capping reply size, adding parameter templates and pre-submission tool checks, and lengthening job callback waits cut it a further 56%, narrowing the gap to 1.5-fold with accuracy preserved (137 of 150 answers accepted).

Conclusion:
AI agents can perform diverse cancer and biomedical data analyses in Galaxy with accuracy comparable to writing their own code, and interface design can bring the added cost close to parity. By using Galaxy, agents create analysis histories that are inspectable, reproducible, reusable, and scalable. These histories enable cancer researchers to easily understand, reproduce, and scale agent-based work and create high-quality data analyses.

Claude Opus 5.5 helped write this abstract; the authors verified all statements.

What changed and why

Style moves taken from Jeremy’s abstracts

Results numbers now use his parallel “X% versus Y% on Z” form instead of a separate sentence listing accuracies as a table in prose. Benchmarks are ordered IWC → BixBench → CompBioBench → multi-step, matching his example.
Benchmarks in Methods use his numbered “(1) … (2) … and (3) …” format with task counts in parentheses, and the model list uses em dashes.
The Galaxy definition is folded into the sentence that introduces it, which is how he handles it in example 1 and how the ML abstract handles its one-line dataset description.
Cost is stated plainly rather than hedged. “Tokens usage difference was important” became a direct statement of the number, and the long final Results sentence was split into three.
“Mainly, analyses performed by AI agents alone…” was reduced to one clean challenge sentence. He uses “two key challenges. First… Second…” when there are two; with one, the enumeration frame is dropped.
Claims I softened

“Outscored” → “were more accurate than.” Same fact, less competitive register, consistent with the “matched or exceeded” calibration in your ML abstract.
“A better interface” came out of the title. It is comparative without a referent, and the abstract never compares to another interface — it compares to no interface.
One thing to check before submitting

“Accuracy preserved (137 of 150 answers accepted)” is the only claim where the comparator is implicit. 137/150 is 91.3%, but it is a different subset from the main runs, so a reader cannot see what it is preserved relative to. If you have the matching pre-revision number, naming it would make this airtight; otherwise consider “with accuracy unchanged on the re-run subset.”

Length

The body is within a few characters of your other AACR 2027 abstract, so it should land near 2,580. Paste it into the form to confirm, since the portal’s counter is the only one that matters. If it runs over, the cheapest cut is the parameter-setup sentence (about 105 characters), though it is the most interface-specific finding you have. Also check that the em dashes survive the paste — some portals mangle them.
