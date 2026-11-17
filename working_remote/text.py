# Paper outline: Nature Methods Brief Communication

Proposed outline for the paper, revised on 17 November 2026 from the 28 October 2026 results release, the error taxonomy in `error_taxonomy.md` and an internal review of the previous version (commit e231916).
This file is not rendered into the manuscript.
The current draft, `brief-communication.qmd`, still follows `outline-brief-communication.md`.
The two conditions are called "Galaxy" and "custom code", as fixed in `outline.md`.
Every number below was recomputed from `data/site/` or read from a table listed under "Where each number comes from", which marks the numbers that no script writes yet.
All numbers stay provisional until one results release is frozen.

Working title: "An agent interface to Galaxy for accurate, inspectable bioinformatics analyses".

## The argument

Galaxy now has an interface that AI agents can operate: a Model Context Protocol (MCP) server and skills.
The agent plans the analysis and interprets the results; Galaxy executes each step and records it.
On three benchmarks of biological data analysis, agents working through Galaxy had broadly similar aggregate scores to agents writing custom code, and every Galaxy run left a structured record of its execution.
The paper is a tool report: the interface is the method, the benchmarks are its validation, and the record is what it adds.

The argument runs in four steps, one per result paragraph, each worded only as far as the results carry it:

1. Aggregate scores were broadly similar in the two conditions on all three benchmarks, and complete multi-step analyses were rare in both.
2. The execution record exposes specific mistakes: in one BixBench question the history shows a header line counted as data.
3. Retrospective diagnostics locate where answers were lost, mostly in the benchmark's own ambiguities and then in missing checks and analytical choices; the execution errors met along the way differ by condition, and the three-attempt procedures tested recover little without the answer key.
4. Galaxy used more tokens, in correct runs too, and each successive interface version measured recorded lower use.

Equivalence is not claimed: no margin was prespecified, and the multi-step interval spans −6.1 to 27.1 points.
A margin chosen now could only be reported as exploratory.

## What this revision changes

| Source | Change | Where |
|---|---|---|
| Review 1 | "No loss of accuracy" replaced by "broadly similar aggregate scores"; equivalence not claimed | Argument, abstract, P3, P7, claim table |
| Review 2 | "Consensus" renamed "at least two attempts passed" and set beside the answer-string vote; "reliability will not come from repetition" removed | P5, Fig. 2b, tables |
| Review 3 | Complete-run success added to the multi-step result; multi-step "at least one" called an output-wise upper bound; design sentence corrected (three models on the multi-step tasks); task weighting stated | P3, P5, tables |
| Review 4 | Official CompBioBench score shown without an interval; the reconstructed key appears only as a labelled diagnostic | P3, Fig. 1b, Supplementary Information |
| Review 5 | Knowledge claim narrowed to the audit labels, counting the 4 unresolved and 7 unreviewed failures; 84 benchmark failures kept apart; the run-log trace moved to the Supplementary Information until reviewed | P5, tables |
| Review 6 | P2 separates what Galaxy already provides from what the MCP server and skills add; inspection claim bounded to the example; UDT caveat | P2, P4 |
| Review 7 | Token cohorts labelled; "successive interface versions showed lower recorded token use"; no claim of preserved acceptance until rescored; wall time added | P6, token table |
| Review 8 | Seven paragraphs, history example before the diagnostics; a plan within 1,200 words comes first | Paragraph outline, budget |
| Review 9 | Checklist split into work required for submission and optional experiments; the margin item reworded | Work before submission |
| Error taxonomy | Execution errors met and recovered from, restricted to the three paper benchmarks, enter P5 and Fig. 2a | P5, tables |

## Paragraph outline

Seven paragraphs: problem, interface, benchmark performance, history example, failure audit and replicate diagnostics, token use, scope.
The bullets hold the content of the longer version, about 1,000 words of main text.
The standard version drops the items listed under "Format and word budget" and runs to about 720 words, so the paper fits the 1,200-word allowance without editorial discretion.
Each paragraph has a title stating its one message and three bullets; the last bullet is its closing sentence.
The titles are drafting labels and come out before submission.
Each pair of numbers is Galaxy first, then custom code.

### Abstract

- Affirm, then turn: agents can carry out bioinformatics analyses, but usually as custom code that is hard to check.
- What we did: built an MCP server and skills through which agents run analyses in Galaxy, and tested them on three benchmarks.
- Result and payoff: aggregate scores were similar, and every Galaxy run left a structured execution record.

Draft, 68 words of the 70 allowed:

> AI agents can carry out bioinformatics analyses, but usually as custom code that is hard to check. Here we present a Model Context Protocol server and skills through which agents run analyses in the Galaxy workbench. On three benchmarks (3,780 runs, four models), agents working through Galaxy scored similarly to agents writing custom code (89.5% versus 88.3% on BixBench), and each Galaxy run left a structured execution record.

### P1. Agents can plan analyses; how they execute them, and how anyone checks the result, is open

- Affirm: AI agents now plan and run whole bioinformatics analyses, and benchmarks such as BixBench and CompBioBench measure how often they reach the accepted answer.
- Turn: the agent usually both plans and executes, writing custom code in an ad hoc environment, where mistakes enter and little is left for a researcher to review.
- Shift: Galaxy already gives people curated, versioned tools, managed compute and a recorded history of every step.
  The question is whether agents can use it as their execution environment, and what that adds and costs.

### P2. An MCP server and skills let agents work in Galaxy: the agent plans and interprets, Galaxy executes and records

- What Galaxy already provides: installed, versioned tools, compute on usegalaxy.org, and histories that keep each job's inputs, tool version, parameters, outputs and state.
- What is new: an MCP server through which an agent finds tools and reads their parameter schemas, submits a job and waits for it in one call, is told when Galaxy resolved the parameters differently from the request, receives a compact result, and opens the history.
  Skills tell the agent how to work with Galaxy; domain guidance given to both conditions is not part of the interface.
  Define the conditions once: in Galaxy every step ran as a Galaxy job, with installed tools or the agent's own code packaged as a user-defined tool (UDT); with custom code the agent installed software and ran its own code.
- Shift: agents completed 1,890 Galaxy runs through this interface, each linked to its history, so the record exists for every answer, not only for the ones someone chose to keep.

### P3. On three benchmarks, aggregate scores were broadly similar in the two conditions

- Evidence: four model configurations ran BixBench-Verified-50 and CompBioBench and three ran ten multi-step IWC analyses, each task three times per condition, 160 tasks and 3,780 runs in all.
  BixBench 89.5% versus 88.3% of answers accepted (difference 1.2 points, 95% interval −1.5 to 4.2).
  CompBioBench 87.0% versus 86.8% of official points; without item-level official grades this difference has no paired interval.
  Multi-step IWC, each task weighted equally: 67.5% versus 58.7% of required results passed (8.8 points, −6.1 to 27.1), and every required result passed in 24.4% versus 23.3% of runs (1.1 points, −16.7 to 21.1).
- Scope: the model mattered more than the condition, with 10 points between models on BixBench and −0.7 to +3.3 points between conditions within a model.
  On the multi-step analyses Galaxy was higher in 7 of 10 tasks; the gap is widest for multiplex tissue imaging (86.4% versus 8.6%) and reverses for 16S amplicon analysis (59.7% versus 90.3%).
- Shift: on these benchmarks the scores did not separate the conditions, so the case for running agents in Galaxy rests on the record it leaves (P4) and on its cost (P6).

### P4. The execution record exposes a mistake that the answer alone hides

- Example: BixBench question bix-52-q7 asks how many rows a methylation filter removes (accepted answer 19,159), and two Galaxy runs answered 19,160.
  Their seven-item histories show why: the filtered table kept its header line, and the line-count step counted it.
- Scope: this example used installed tools; a step run as a UDT, as in 844 of 1,200 CompBioBench Galaxy runs, is checked by reading the agent's code, although its inputs, outputs and job state are still recorded.
  Read back retrospectively, the history showed the deciding mistake in 13 of 27 Galaxy BixBench failures not attributed to the benchmark (one reader); whether a researcher would catch such mistakes before an answer is reported is untested.
- Shift: the record turns a wrong number into a chain of datasets and jobs that can be opened, so checking an agent's analysis can start from its history instead of a rerun.

### P5. Retrospective diagnostics locate where answers were lost, and three attempts recover little without the key

- Failure audit: of 133 wrong BixBench answers, the audit attributes 84 to an under-specified task or scoring rule.
  Of the other 49 it assigns 31 to missing validation (4 with the cause unresolved), 6 to the platform or harness (all Galaxy) and 5 to model knowledge, and 7 await review; failures assigned to missing validation outnumbered those assigned to incorrect biological or statistical concepts.
  In 34 of the 49, another attempt by the same model in the same condition was correct.
- Execution errors met along the way, on all three benchmarks: 87.6% versus 72.6% of correct runs met at least one failed command or rejected request and still reached the accepted answer.
  Custom-code runs more often met software that was missing or would not install (20.9% versus 46.9% of correct runs) and compute limits (6.4% versus 16.6%), whereas Galaxy runs more often had requests rejected by the interface, such as parameters (55.6% versus 4.3%).
- Replicate diagnostics: on BixBench at least two of three attempts passed in 90.0% versus 90.5% of groups, but a vote on the answer strings returned an accepted answer in 82.5% versus 80.0% and abstained in 11% versus 12%.
  At least one attempt passed in 93.0% versus 92.0%; picking that attempt needs the answer key, so this is an upper bound, not a procedure.
  These diagnostics point to checks of intermediate results, which the record makes possible and which only a prospective test can evaluate.

### P6. Galaxy used more tokens, and successive interface versions recorded lower use

- Evidence, benchmark runs: Galaxy used 4.07 times the tokens of custom code on BixBench and 2.48 times on CompBioBench (October main runs, four models), and 1.47 times on the multi-step analyses (three models).
  Counting only runs with an accepted answer, the BixBench ratio is 3.8, so the overhead is present in correct runs.
  On the multi-step analyses a Galaxy run took a median of 233 minutes against 75, with its jobs run on the public usegalaxy.org server.
- Development series, separate BixBench batches: in a July GPT-5.5 batch, Galaxy runs took 2.66 times as many agent turns, each carrying 2.20 times as much cached context.
  Successive interface versions showed lower recorded token use: GPT-5.5 from 5.48 (prompts and skills) to 2.81 (MCP execution), and GPT-5.6 Sol from 3.45 (MCP execution) to 2.42 (compact replies, one replicate) and 1.53 (longer waits).
  The CLI version and replicate coverage also changed between batches, and acceptance has not been rescored under one rule, so no change is credited with preserving accuracy.
- Shift: in these batches token use responded to interface engineering, and the error map names the next targets: tool lookups made without naming a history (1,251 calls in 545 runs) and rejected parameters.

### P7. What the interface is, its limits, and the next test

- What it is: an interface through which agents carry out biological analyses in Galaxy, with broadly similar aggregate benchmark scores to custom code and a structured record of execution.
- Limits: four model configurations (three on the multi-step tasks), one harness, prompts and compute resources that differ between conditions, IWC references built in Galaxy, failure causes audited on one benchmark, and replicate figures estimated retrospectively from existing runs.
- Next test: a prospective validation step that reads the history before an answer is reported, scored by the wrong answers it catches and the right answers it rejects.

### Words and panels

| Paragraph | Words, standard version | Words, longer version | Figure panel |
|---|---|---|---|
| P1 | 80 | 90 | |
| P2 | 130 | 150 | 1a |
| P3 | 120 | 170 | 1b |
| P4 | 95 | 130 | 1c |
| P5 | 135 | 210 | 2a, 2b |
| P6 | 110 | 170 | 2c |
| P7 | 50 | 80 | |
| **Total** | **720** | **1,000** | |

## How each point is worded so that the results support it

Each row gives a point as first proposed, the wording the outline uses, and the evidence that carries it.

| Point as first proposed | Wording the results support | Evidence |
|---|---|---|
| Agents lose no accuracy through Galaxy | Aggregate scores were broadly similar in the two conditions | Point estimates 89.5 versus 88.3, 87.0 versus 86.8 and 67.5 versus 58.7; intervals cross zero but no margin was prespecified, so equivalence is not shown; the multi-step interval spans −6.1 to 27.1 |
| Agents complete multi-step analyses through Galaxy | Galaxy runs passed more required results on the multi-step tasks; complete analyses were rare in both conditions | 67.5% versus 58.7% of required results; every result passed in 24.4% versus 23.3% of runs (interval −16.7 to 21.1) |
| CompBioBench interval from the reconstructed key | The official score has no paired interval; the reconstructed key is a separate, labelled diagnostic | Official 87.0 versus 86.8 favours Galaxy slightly; reconstructed item matches 86.6 versus 88.3 (interval −3.8 to 0.5) favour custom code |
| A consensus adds little | At least two attempts passed about as often as a single attempt; an answer-string vote returned an accepted answer less often than a single attempt on BixBench and abstained in 11–12% of groups | 90.0 / 90.5 against 89.5 / 88.3; vote 82.5 / 80.0, abstained 11 / 12; agreement in correctness is not agreement in answers |
| Reliability will not come from repetition | Not claimed; the evidence covers these three-attempt procedures only | Two procedures tested, both retrospectively |
| A correct answer was usually produced | At least one of three attempts passed in most groups; selecting it needs the key, so it is an upper bound | 93.0 / 92.0 on BixBench; on the multi-step tasks 86.5 / 70.9 per result, which can combine results from different runs and is not an achievable complete analysis |
| Model knowledge is rarely the limit | In the BixBench audit, failures assigned to missing validation outnumbered those assigned to incorrect biological or statistical concepts | 31 against 5 of the 49 failures not attributed to the benchmark, with 6 platform or harness and 7 awaiting review; 84 of 133 attributed to the benchmark and kept apart; a correct sibling attempt (34 of 49) does not show that knowledge played no part |
| Wrong answers come from analytical choices and slips (run-log trace) | Supplementary Information only, until a second rater reviews it | The trace assigns 10 of the 49 to a wrong concept, 17 to other analytical choices and 18 to execution slips, and reclassifies 19 of the audit's 31 missing-validation runs as deliberate analytical choices |
| Galaxy makes fewer execution errors | Galaxy runs met different execution errors and reached the accepted answer about as often | Correct runs that met an error 87.6% versus 72.6%; software not available 20.9% versus 46.9%; compute limits 6.4% versus 16.6%; rejected parameters 55.6% versus 4.3%; three benchmarks, CompBioBench outcome by the reconstructed key |
| A researcher would catch the header mistake; no code to read | The recorded artifacts expose this discrepancy; a UDT step is checked by reading the agent's code | Header row verified in three public histories; 13 of 27 Galaxy failures visible on retrospective reading by one reader; UDTs in 844 of 1,200 CompBioBench Galaxy runs; detection by people untested |
| Correct and incorrect runs cost the same tokens | The token overhead is present in correct runs | Correct runs alone cost 3.8 times custom code; median incorrect Galaxy run 1.85 against 2.15 million for a correct one, but the mean incorrect run used 2.2 times the mean correct one |
| Every interface change lowered the token cost | Successive interface versions showed lower recorded token use | 5.48 to 2.81 and 3.45 to 2.42 to 1.53 in sequential batches; CLI 0.146.0 to 0.156.0; the compact-replies stage is one replicate |
| Accepted answers were retained (137 after, 136 before) | Not claimed until both batches are rescored under one rule | Published optimized batch 137 of 150; current standard Sol Galaxy runs 139 of 150; 140 of 150 only under the revised PhyKIT sensitivity calculation |

## Numbers behind P3 to P6

Benchmark scores (P3).

| Benchmark | Score | Galaxy | Custom code | Difference, 95% interval | Runs per condition |
|---|---|---|---|---|---|
| BixBench-Verified-50 | Answers accepted | 89.5% | 88.3% | 1.2 (−1.5 to 4.2) | 600 |
| CompBioBench | Official points | 87.0% | 86.8% | 0.25, no paired interval | 1,200 (12 submissions) |
| CompBioBench, diagnostic | Reconstructed item matches | 86.6% (1,039) | 88.3% (1,059) | −1.7 (−3.8 to 0.5) | 1,200 |
| IWC multi-step | Required results passed, tasks weighted equally | 67.5% | 58.7% | 8.8 (−6.1 to 27.1) | 90 |
| IWC multi-step | Runs with every required result passed | 24.4% | 23.3% | 1.1 (−16.7 to 21.1) | 90 |

Execution errors recovered from, by subcategory, on the three paper benchmarks: correct runs that met at least one, and their share of correct runs with an event log (1,587 Galaxy, 1,610 custom code).
A run is correct when its BixBench answer was accepted, its CompBioBench answer matches the reconstructed key (a diagnostic), or every required multi-step result passed.
`error_taxonomy.md` also pools the shorter IWC workflow tasks (4,008 logs), which gives 88.3% versus 73.5%; the paper uses the three-benchmark cohort below.

| Subcategory | Galaxy | Custom code |
|---|---|---|
| Software not available | 331 (20.9%) | 755 (46.9%) |
| Interface or API request rejected | 740 (46.6%) | 153 (9.5%) |
| Parameters rejected | 882 (55.6%) | 70 (4.3%) |
| Agent's own code failed | 625 (39.4%) | 208 (12.9%) |
| Data or file handling | 609 (38.4%) | 526 (32.7%) |
| Analysis tool failed | 332 (20.9%) | 70 (4.3%) |
| Compute limit reached | 102 (6.4%) | 268 (16.6%) |
| Platform, network or sandbox | 226 (14.2%) | 244 (15.2%) |
| **Any execution error** | **1,391 (87.6%)** | **1,169 (72.6%)** |
| Any, without the interface's own parameter check | 1,323 (83.4%) | 1,169 (72.6%) |

Causes of the 133 wrong BixBench answers under the audit labels, which the main text uses.

| Audit label | Galaxy (63) | Custom code (70) |
|---|---|---|
| Task or scoring ambiguity | 36 | 48 |
| Missing validation, cause assigned | 14 | 13 |
| Missing validation, cause unresolved | 1 | 3 |
| Platform or harness | 6 | 0 |
| Model knowledge | 1 | 4 |
| Awaiting review | 5 | 2 |

The same 49 failures not attributed to the benchmark under the run-log trace, which goes to the Supplementary Information until reviewed.

| Trace category | Galaxy (27) | Custom code (22) |
|---|---|---|
| Knowledge: wrong parameter or threshold | 6 | 4 |
| Knowledge: wrong biological or statistical concept | 3 | 7 |
| Knowledge: wrong method, misread question or added step | 3 | 4 |
| Execution: data or file handling (header row, sort, columns, files) | 6 | 3 |
| Execution: tool version or implementation differs from the reference | 2 | 3 |
| Execution: no answer returned, or result accepted without a check | 4 | 0 |
| Unclear | 3 | 1 |

The trace places the audit's 31 missing-validation runs as 19 knowledge and 12 execution, its 6 platform or harness runs as execution, its 5 knowledge runs as knowledge, and its 7 runs awaiting review as 3 knowledge and 4 unclear.

Scoring three attempts, in percent of groups.
A group is the three attempts of one model on one question in one condition; on the multi-step tasks it is the three attempts of one model on one required result.

| Benchmark | Single attempt | At least two attempts passed | Answer vote accepted | Answer vote abstained | At least one attempt passed (upper bound) |
|---|---|---|---|---|---|
| BixBench-Verified-50, 200 groups | 89.5 / 88.3 | 90.0 / 90.5 | 82.5 / 80.0 | 11.0 / 12.0 | 93.0 / 92.0 |
| CompBioBench, reconstructed key, 400 groups | 86.6 / 88.3 | 87.5 / 89.8 | 87.5 / 89.8 | 4.8 / 2.5 | 92.5 / 96.0 |
| IWC multi-step, 261 groups | 67.5 / 58.7 | 69.0 / 58.1 | not defined | not defined | 86.5 / 70.9, output-wise |

Agreement in correctness: groups by the number of attempts that passed.

| Benchmark | All 3 passed | Exactly 2 | Exactly 1 | None |
|---|---|---|---|---|
| BixBench-Verified-50, 200 groups | 171 / 165 | 9 / 16 | 6 / 3 | 14 / 16 |
| CompBioBench, reconstructed key, 400 groups | 319 / 316 | 31 / 43 | 20 / 25 | 30 / 16 |
| IWC multi-step, 261 groups | 122 / 124 | 59 / 28 | 46 / 35 | 34 / 74 |

Tokens per BixBench run by outcome, October main runs, in millions.

| Measure | Galaxy | Custom code | Ratio |
|---|---|---|---|
| All runs, total tokens | 2,782.5 | 684.3 | 4.07 |
| Correct runs only, mean per run | 4.12 | 1.09 | 3.79 |
| Median correct run | 2.15 | 0.46 | |
| Median incorrect run | 1.85 | 0.67 | |
| Share of tokens spent on correct runs | 79.6% | 84.2% | |

Token cohorts in P6, all BixBench, with the Galaxy-to-custom-code ratio and the Galaxy acceptance each batch recorded.
The three GPT-5.6 Sol ratios share one custom-code batch (35.51 million tokens per 50-task replicate).

| Cohort | Model, replicates | Interface | Ratio | Galaxy accepted |
|---|---|---|---|---|
| July 6 batch | GPT-5.5, 3 | Prompts and skills, before MCP execution | 5.48 | 139 of 150 |
| 12 October snapshot | GPT-5.5, 3 | MCP execution | 2.81 | 137 of 150, scored at the time |
| 12 October snapshot | GPT-5.6 Sol, 3 | MCP execution | 3.45 | 136 of 150, scored at the time |
| Optimization batch | GPT-5.6 Sol, 1 | Compact replies, parameter templates, UDT checks | 2.42 | Not reported |
| Optimization batch | GPT-5.6 Sol, 3 | Plus longer waits | 1.53 | 137 of 150 published; 140 under the revised PhyKIT rule (sensitivity only) |
| October main runs, current scoring | GPT-5.6 Sol, 3 | Standard | | 139 of 150 |

From compact replies to longer waits, mean wait calls per replicate fell from 481 to 78 and model requests from 1,799 to 1,332.
The early ratios of about 20 and 8 are author estimates without deposited run records; the series in the paper starts at 5.48.

## Display items

Two figures of three panels each.
Figure 1 shows the interface, its benchmark scores and the record it leaves; Figure 2 shows the retrospective diagnostics and the cost.

| Figure | Panel | Shows | Supports | Exists today |
|---|---|---|---|---|
| 1. Interface, scores and record | a | Agent plans and interprets; MCP server and skills; Galaxy executes and records; the two conditions | P2 | Fig. 1a; redraw around the division of labour |
| 1 | b | Galaxy minus custom code with 95% intervals: BixBench, multi-step required results and multi-step complete runs; CompBioBench official as an open marker without an interval; one point per model and one pooled | P3 | Fig. 1d, pooled only and with the IWC workflow tasks; rebuild |
| 1 | c | The seven-item history of bix-52-q7, with the header row and the line count marked beside the accepted and reported answers | P4 | Not built |
| 2. Diagnostics and cost | a | Left, share of correct runs that met each execution-error subcategory, by condition; right, audit causes of the 133 wrong BixBench answers, including unresolved and awaiting review | P5 | New, from `data/error_taxonomy/` and the failure ledger; replaces Fig. 2a |
| 2 | b | Single attempt, at least two attempts passed, answer vote (accepted and abstained) and at least one attempt passed, per benchmark and condition; CompBioBench rows labelled "reconstructed key, diagnostic"; "at least one" drawn as an upper bound | P5 | Fig. 2b; add the vote and the multi-step rows |
| 2 | c | Token ratios with each cohort labelled: October main runs by benchmark, correct runs only, then the development series by model from 5.48 | P6 | Fig. 2c and Supplementary Fig. 6; merge, drop the estimated 20 and 8 |

Panel 1b plots differences, not paired bars.
The reconstructed CompBioBench difference and its interval (−3.8 to 0.5) go in a labelled diagnostic comparison in the Supplementary Information, never on panel 1b.

The Supplementary Information takes the rest: per-model accuracy, the multi-step analyses by task and model with complete-run success, the ten shorter IWC workflow tasks with their token ratio (0.96), the independent comparison of the IWC 002 RNA-seq output with the raw reference (13 genes each, 12 shared), the reconstructed CompBioBench comparison, raw against reviewed BixBench scoring, UDT use by benchmark, the selected reruns and trial runs, the full error taxonomy, the run-log trace of the 49 BixBench failures, agreement tables, tokens by outcome, wall time and the main-run token totals.

## Format and word budget

A Brief Communication allows 1,200 words including abstract, references and figure legends, or 1,600 at the editor's discretion.
This plan is written to fit 1,200; the discretionary 1,600 is an option to request, not a premise.

| Element | Journal limit | Standard version | Longer version, if 1,600 is granted |
|---|---|---|---|
| Abstract | 70 words, unreferenced | 68 | 68 |
| Main text | No sections or subheadings | 7 paragraphs, about 720 | 7 paragraphs, about 1,000 |
| Figure legends | Counted | About 180 for 2 figures | About 250 |
| References | About 20 as a guideline; counted | 15, about 225 | 18, about 270 |
| **Total** | **1,200 (1,600)** | **About 1,195** | **About 1,590** |
| Display items | 2 figures or tables, 3 at discretion | 2 figures of 3 panels each | Same |
| Online Methods | Required, with subheadings; outside the count | All implementation detail and disclosures | Same |

The journal lists software platforms and practical improvements to existing tools as Brief Communication material.
A paper that reads as a comparison of established tools may be redirected to the longer Analysis format, so keep the interface as the subject.

The standard version is the outline as written minus these items, about 280 words, moved to the Supplementary Information or Methods.
Never cut P2's sentence on what the interface adds to Galaxy.

1. P4: the retrospective count, 13 of 27 (about 35 words).
2. P3: the sentences on model differences and on individual tasks (about 50).
3. P5: the sibling-attempt count, 34 of 49, and the closing sentence, and the execution-error bullet reduced to one sentence (about 75).
4. P6: the turns-and-context sentence and the closing list of targets (about 60).
5. P7: the limits list, reduced to one clause that points to Methods (about 30).
6. P2: the condition definitions shortened, keeping what is new (about 20).
7. Every paragraph: tighter prose than the bullets (the rest).

Adding to the longer version, once reviewed: the run-log trace of the 49 BixBench failures in P5, and the multi-step replicate diagnostics in P5.

Title options:

- "An agent interface to Galaxy for accurate, inspectable bioinformatics analyses" names the tool and what is new; the review recommends it.
  If "accurate" reads as more than the 24.4% complete-run success supports, drop it.
- "AI agents can perform accurate bioinformatics analyses through a computational workbench" is the candidate adapted from Jeremy Goecks's title comment.

## Which IWC results the paper reports

The repository holds two sets of ten IWC tasks, and the paper's third benchmark is the harder set.

| | IWC workflow tasks | IWC multi-step tasks |
|---|---|---|
| Task | Reproduce one IWC workflow of 2 to 27 tool steps | Carry a full analysis from raw data to 8–12 scored results; the task text names no software |
| Source file | `data/site/iwc/data/results.json` | `data/site/iwc/long-chain/data/results.json` |
| Runs | 240, four models | 180, three models (GPT-5.5 not run) |
| Galaxy versus custom code | 99.0% versus 95.3% mean output agreement | 67.5% versus 58.7% of required results passed; 24.4% versus 23.3% of runs with every result passed |
| Role in the paper | Supplementary Information, with its token ratio and the RNA-seq output comparison | The third benchmark: abstract and P3, P5, P6 |

Five of the ten workflow tasks are at ceiling in both conditions, so that set cannot separate conditions or models.
Counting it as well would give 170 tasks and 4,020 runs.

## Work before submission

### Required for submission

These carry the claims the outline makes; without them a scoped interface paper cannot be reviewed.

- [ ] Release the interface: the MCP server, skills and prompts, under an open licence, with a version and a DOI.
  The benchmark repository is private today.
  State which interface version each benchmark's runs used: templates, compact replies and longer waits came in the later Sol batch.
- [ ] Freeze one results release and regenerate every number in the text from it.
- [ ] Integrate the multi-step IWC tasks into `data/results_manifest.csv` and the figure build.
  The current package still describes the 3,840-run design with the shorter IWC workflow tasks; the multi-step tables live on the local branch `iwc-multistep-snapshots`.
- [ ] Write scripts in `analysis/` for every quantity introduced for this outline: the multi-step intervals and complete-run success, the multi-step replicate diagnostics, the reconstructed CompBioBench interval, the error map restricted to the three benchmarks, tokens by outcome, and the bix-52-q7 history check.
  Until then these numbers do not meet the repository's tracing rule.
- [ ] Use one scoring definition per benchmark across the accuracy, replicate, error and token tables, and label every CompBioBench item-level number as the reconstructed key.
- [ ] Rescore the Sol token batches under one rule before saying anything about acceptance across interface versions.
- [ ] Review the error taxonomy: the rules that type the execution errors, and the audit labels the main text uses.
  Decide whether the run-log trace enters the Supplementary Information; it needs a second rater on a sample first.
- [ ] Archive the histories with a DOI, and say what the record keeps for a UDT.
- [ ] Complete the reference list: `references.bib` holds 12 checked entries, and every added entry must be checked against its source.
- [ ] Send a presubmission enquiry asking the editor to confirm Brief Communication over Analysis.
- [ ] If an equivalence margin is reported, describe it as exploratory; it cannot become prespecified now.
- [ ] Claim "rerunnable" only if a sample of histories is rerun without an agent; otherwise drop the word.

Disclosures in Methods:

- [ ] Every replaced run, the reason, and whether replacement depended on the outcome.
- [ ] The 16 GPT-5.6 Luna trial runs that count as run 1 in both conditions on eight multi-step tasks, and how they are treated.
- [ ] Uneven model coverage: GPT-5.5 did not run the multi-step tasks.
- [ ] Prompts that differ between conditions (707 against 366 median words on BixBench, from the Word draft), and which skills belong to the interface rather than to the domain guidance both conditions received.
- [ ] Resources: on the multi-step tasks the Galaxy agent worked from a container with 8 GB of memory and ran its jobs on usegalaxy.org, and the custom-code agent had 64 GB and internet access.
- [ ] IWC references built by running the IWC workflows in Galaxy.
- [ ] Both BixBench scorings; the sign of the difference rests on one question, bix-45-q1.
- [ ] Runs that searched the web for the question text (bix-14-q1) or opened the benchmark's dataset page (bix-43-q2).

### Optional: would support further claims

None of these blocks a carefully scoped interface paper; each would let the paper say something it does not say now.

- [ ] A prospective validation step: give a person or an agent the history before the answer is reported, and count the wrong answers caught and the right answers rejected.
  This is the experiment that would turn P4 and P5 from retrospective diagnostics into a method.
- [ ] GPT-5.5 on the multi-step tasks, so that all four models cover all three benchmarks; reporting the uneven coverage clearly is enough without it.
- [ ] Replacing the 16 trial runs, only with a documented protocol reason, reporting the original results beside the replacements.
- [ ] A broader failure audit: CompBioBench's 301 wrong answers and the multi-step causes.
- [ ] Item-level official grades for CompBioBench, which would allow a paired interval on the official score.
- [ ] A controlled interface comparison with model, CLI, tasks and scoring fixed, needed only to credit individual interface changes with the token reductions.
- [ ] Replay of a sample of histories without an agent, needed only to claim the analyses are rerunnable.

## Where each number comes from

| Numbers | Source | On the paper branch |
|---|---|---|
| Tasks and runs per benchmark | `data/results_manifest.csv`; multi-step runs in `data/site/iwc/long-chain/data/results.json` | Yes |
| BixBench and CompBioBench scores, interval and per-model values | `figures/benchmark_results_summary/fig1_performance/dataset/source_data.csv` | Yes |
| Multi-step results passing and complete-run success, per model and pooled | `data/accuracy_summary.csv` and `data/accuracy_by_model.csv`, written by `analysis/accuracy.py` | Yes |
| Multi-step intervals (both scores), per-task values, tokens, wall time and trial-run flags | `data/iwc_long_chain/derived/pooled.csv`, `by_task.csv` and `runs.csv` (snapshot of 7 November) | No: local branch `iwc-multistep-snapshots` |
| Why the imaging task differs between conditions | Task 9 page of the results website, "What Galaxy added" | No: archived on `iwc-multistep-snapshots` |
| Single attempt, at least two passed, answer vote and at least one passed, BixBench and CompBioBench; groups by number passed | `s3_repeatability/dataset/source_data.csv` | Yes |
| The same for the multi-step analyses, per required result | Computed on 17 November from the multi-step results file | No script yet |
| CompBioBench reconstructed key and its interval | `fig1_performance/dataset/item_scores.csv`; interval recomputed on 16 November | Counts yes; interval not yet written by a script |
| Audit labels of the 133 BixBench failures, and attempts with another pass | `fig2_interface/dataset/bixbench_current_failures.csv`, `fig2_interface/dataset/source_data.csv` and `RESULTS.md` | Yes |
| Run-log trace of the 49 BixBench failures, history visibility and sibling attempts | `data/error_taxonomy/bixbench_agent_failures_traced.csv` | Written, not yet committed; awaits author review |
| Execution errors recovered from, three benchmarks | Computed on 17 November from `data/error_taxonomy/execution_subcategories.csv` and `run_summary.csv`, written by `analysis/error_taxonomy.py`; the restriction to three benchmarks has no script yet | Written, not yet committed |
| Tool lookups made without a history, three benchmarks | `data/error_taxonomy/execution_errors.csv`, same restriction | Written, not yet committed |
| bix-52-q7 answers and labels | `data/site/bixbench/data/results.json`; the failure ledger above | Yes |
| bix-52-q7 histories: items, line counts and header row | Three public histories opened through the usegalaxy.org API on 17 November | No script yet |
| UDT use and history links | `s1_execution/dataset/run_histories.csv` and `source_data.csv`; multi-step history links in `runs.csv` above | Yes, except the multi-step links |
| Token ratios on BixBench, CompBioBench and the IWC workflow tasks | `s6_token_usage/dataset/source_data.csv` | Yes |
| Tokens by outcome on BixBench | Computed on 17 November from per-run `usage` in `data/site/bixbench/data/results.json` | No script yet |
| Agent turns and cached context, July batch | `s7_token_drivers/dataset/source_data.csv` | Yes |
| Token stages, wait calls, model requests and acceptance | `data/token_optimization_rounds.csv`, `fig2_interface/dataset/source_data.csv` and `optimization_key_sensitivity.csv`; current standard Sol acceptance and CLI versions from `RESULTS.md` | Yes |
| Interface features | `brief-communication.qmd` Methods and `error_taxonomy.md` (the parameter-resolution check) | Yes; versions per benchmark still to be stated |
| Prompt lengths | `outline.md`, from the Word draft | No script |
| Format limits | `outline-brief-communication.md`, from the journal's content-type guidance | Yes |
