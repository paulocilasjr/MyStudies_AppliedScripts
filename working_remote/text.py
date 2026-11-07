Written for: AACR 2027 abstract reviewers and program committee.

The abstract is ready at 2,581 of 2,600 characters, counting the title, headings and disclosure line without spaces. I checked every number against the repository data. Your draft and the pasted revision had a few wrong claims, which I've fixed (listed below).

Agents as Virtual Users: Improving How AI Agents Use the Galaxy Workbench for Cancer Data Analysis

Paulo Cilas Morais Lyra Jr., Junhao Qiu, Alyssa F. Pybus, Isis Narvaez-Bandera, Jeremy Goecks
H. Lee Moffitt Cancer Center & Research Institute, Tampa, FL

Purpose:
Cancer researchers are increasingly using AI agents such as ChatGPT Codex to perform data analyses, from multi-omic profiling to single-cell analysis and even machine learning. However, analyses by agents alone are often difficult to understand and reproduce because agents generate a large amount of code. To address this limitation, we made AI agents virtual users of Galaxy, a computational biomedical workbench built for accessible, reproducible, and scalable analysis. We benchmarked agents in Galaxy to measure what the combination achieves, find where the interface fails, and test fixes.

Methods:
We evaluated how accurately AI agents perform data analysis tasks using either Galaxy or their own code. We used four large language models—GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, and DeepSeek V4 Pro—in a common Codex agent harness. The 160 main tasks came from three sources: (1) Intergalactic Workflow Commission (IWC; 10 tasks), (2) BixBench-Verified-50 (50 tasks), and (3) CompBioBench (100 tasks). Each model, task, and condition was run in triplicate, yielding 3,840 primary runs. Three models also performed 10 harder multi-step IWC analyses (180 runs). We classified wrong answers and failed Galaxy requests and measured token use across interface versions.

Results:
Agents using Galaxy matched or exceeded the accuracy of agents writing their own code, scoring higher in 12 of 15 model-benchmark comparisons: 99.0% versus 95.3% on IWC, 89.5% versus 88.3% on BixBench, 87.0% versus 86.8% on CompBioBench, and 67.5% versus 58.7% on multi-step IWC analyses (references made in Galaxy). Every Galaxy run produced a history linking the answer to its tools, parameters, data, and agent code. Galaxy itself caused few wrong answers: of 133 BixBench failures, 108 reflected task specification or missing validation in both conditions, and only 6 the platform or harness. Interface problems appeared instead as failed requests, such as jobs failing without a diagnostic (1,339), tool lookups lacking history context (1,121), and parameter errors (981). Galaxy's main cost was token use, 1.0- to 4.1-fold that of custom code, and interface changes reduced it. On BixBench, an MCP server that submits jobs, waits, and returns compact results had already cut GPT-5.5 tokens by 55%. Capped replies, parameter templates, pre-submission tool checks, and longer job waits then cut GPT-5.6 Sol tokens a further 56%, to 1.5-fold custom code, with similar accuracy (137 versus 136 of 150 correct).

Conclusion:
AI agents can perform diverse cancer and biomedical data analyses in Galaxy with accuracy comparable to writing their own code. By using Galaxy, agents create analysis histories that cancer researchers can inspect, reproduce, reuse, and scale. Using agents as virtual users reveals where the interface fails and how to fix it, lowering the added cost.

Claude Opus 5.5 helped write this abstract; the authors verified all statements.

Wrong claims I fixed

"Mostly missing validation (108 of 133)": missing validation accounts for only 31 of the 108. The other 77 are task-specification errors. Your draft had the same mistake.

"Most often parameter setup errors (n=981)": three classes are larger:

tool runtime errors: 1,458
jobs failing with no diagnostic: 1,339
lookups lacking history context: 1,121
The 981 also combines two classes (765 + 216). I changed "most often" to "such as".

"Up to 4.1-fold more tokens" and "two revisions closed most of this gap":

4.1 is the pooled BixBench ratio. Per model it goes up to 6.3-fold (Luna), and on IWC Galaxy used slightly fewer tokens (0.96).
The main runs already used the MCP server: GPT-5.5's 55% cut (5.5-fold → 2.8-fold) happened before them.
Only the October changes came afterward, and they were tested only on Sol on BixBench (3.4-fold → 1.5-fold).
The text now gives that order.

"Accuracy preserved (137 of 150)": the missing comparison is Sol before the October changes, 136 of 150.

"Efficient interface" (title) and "close to parity" (conclusion): 1.5-fold is not parity, and multi-step Galaxy runs took 3.1 times longer. I used "Improving" instead.

Multi-step references: they were built by running the workflows in Galaxy, which can favor Galaxy. That difference is also not statistically clear (−6.1 to 27.1). I added "(references made in Galaxy)" as a short caveat.

How the text follows Jeremy's style (only example 1 reached me; example 2 wasn't attached):

I kept his sentences word for word where they fit: the opening, "We evaluated…", the model list, the triplicate line and "By using Galaxy, agents create analysis histories…".
I used his "matched or exceeded" wording and his "X% versus Y% on Z" pattern, in his order: IWC, BixBench, then CompBioBench.
Short topic sentences lead each point: "Galaxy itself caused few wrong answers." and "Galaxy's main cost was token use."
Before you submit

AI used in the analysis: AACR wants any AI used to conduct the research described in Methods. If Codex or Claude helped analyze results (my earlier draft said so), that sentence needs about 75 characters and only 19 are left. The multi-step caveat or "and even machine learning" could go to make room.
Headings: if the portal doesn't count them, the total is 2,546. Paste the text into the portal to confirm the count, and check that the em dashes come through.
