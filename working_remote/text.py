Combining the three runs helps little when you take the majority answer: at most 2.2 points. Counting a task as correct if any of the three runs got it right helps much more: 3.5 to 12.5 points. So validating results matters more for accuracy than consensus does. Galaxy gains less from both rules because its three runs agree with each other more often.

Benchmark	Rule	Galaxy	Custom code	Galaxy − custom code (95% CI)
BixBench	One run	89.5	88.3	+1.2 (−1.2 to 4.0)
Consensus (≥2 of 3 correct)	90.0	90.5	−0.5 (−2.5 to 1.0)
Validation (≥1 of 3 correct)	93.0	92.0	+1.0 (−1.0 to 3.5)
CompBioBench*	One run	86.6	88.3	−1.7 (−3.8 to 0.5)
Consensus	87.5	89.8	−2.3 (−5.5 to 0.8)
Validation	92.5	96.0	−3.5 (−5.8 to −1.5)
IWC*	One run	79.2	72.5	+6.7 (0.0 to 15.8)
Consensus	80.0	70.0	+10.0 (0.0 to 20.0)
Validation	85.0	85.0	0.0 (−10.0 to 12.5)
Gain over one run, in percentage points:

Consensus, Galaxy	Consensus, custom code	Validation, Galaxy	Validation, custom code
BixBench	+0.5	+2.2	+3.5	+3.7
CompBioBench	+0.9	+1.5	+5.9	+7.8
IWC	+0.8	−2.5	+5.8	+12.5
Mean of the 3 benchmarks	+0.8	+0.4	+5.1	+8.0
What this shows:

Consensus adds little. Most tasks are unanimous: all three runs right or all three wrong. Only the split cases can change, and Galaxy has fewer of them: 15 vs 19 on BixBench, 51 vs 68 on CompBioBench and 5 vs 9 on IWC. Galaxy's runs are more repeatable, so a majority has less to fix.
Validation is the bigger lever. Many errors happen in only one of the three runs. If the correct run could be recognized, accuracy would reach 85–96%. Galaxy histories make each run's tools and parameters inspectable, which is what validation needs. We haven't measured whether researchers actually validate faster with them, so present this as a potential benefit.
Effect on the comparison:
With consensus, Galaxy's IWC lead widens from 6.7 to 10 points, and BixBench becomes a tie.
With validation the two conditions converge, because custom code varies more between runs and so gains more.
Picking the answer the agent repeated (taking the identical answer returned by 2 of 3 runs, the version that could actually be automated) is worse than one run on BixBench: 82.5 vs 89.5 for Galaxy and 80.0 vs 88.3 for custom code. Correct numeric answers are often written differently, for example 0.02097 and 0.020971, so no answer wins a majority. A working consensus would need tolerance-aware matching. On CompBioBench, whose answers are mostly categories, it equals the consensus row.
*Only the BixBench one-run row matches a main result. The other two rows use the per-replicate correctness the package records:

CompBioBench uses the reconstructed answer key, a diagnostic that favors custom code. The official score (87.0 vs 86.8) is reported per replicate, so it can't be combined across runs.
IWC counts a run as correct only at an agreement of 0.99 or higher.
Don't mix these rows with the abstract's accuracy numbers.

Per model (one run / consensus / validation, %):

Galaxy	Custom code
BixBench, DeepSeek V4 Pro	83.3 / 82.0 / 90.0	82.7 / 84.0 / 88.0
BixBench, GPT-5.5	93.3 / 94.0 / 94.0	92.0 / 92.0 / 94.0
BixBench, GPT-5.6 Luna	88.7 / 90.0 / 94.0	89.3 / 94.0 / 94.0
BixBench, GPT-5.6 Sol	92.7 / 94.0 / 94.0	89.3 / 92.0 / 92.0
CompBioBench, DeepSeek V4 Pro	84.7 / 86.0 / 93.0	85.0 / 87.0 / 95.0
CompBioBench, GPT-5.5	86.0 / 87.0 / 92.0	88.3 / 89.0 / 96.0
CompBioBench, GPT-5.6 Luna	83.7 / 83.0 / 89.0	86.3 / 87.0 / 96.0
CompBioBench, GPT-5.6 Sol	92.0 / 94.0 / 96.0	93.3 / 96.0 / 97.0
IWC, DeepSeek V4 Pro	93.3 / 100 / 100	80.0 / 80.0 / 100
IWC, GPT-5.5	70.0 / 70.0 / 80.0	63.3 / 60.0 / 70.0
IWC, GPT-5.6 Luna	73.3 / 70.0 / 80.0	73.3 / 70.0 / 80.0
IWC, GPT-5.6 Sol	80.0 / 80.0 / 80.0	73.3 / 70.0 / 90.0
For the abstract: these results don't add a clear Galaxy advantage, and only 10 characters are free. They fit the manuscript or talk better, for example: "Validating three runs would raise accuracy by 3.5–12.5 points, against at most 2.2 for a majority."

The script is analysis/summarize_consensus.py. It writes data/consensus/consensus_accuracy.csv, and the folder's README explains each rule and its limits. It reproduces the package's existing repeatability table exactly, and the package verifier still passes. Nothing is committed yet.
