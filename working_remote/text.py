Galaxy agent benchmark: Brief Communication outline
Nov 16, 2026 · @Paulo Lyra
What changed from the previous outline
The previous outline had the right claim, but it would not fit the format and its main differentiator had no evidence behind it. This version keeps the claim, cuts ten paragraphs to eight, and gives each paragraph a number to stand on.
Issue
Previous outline
This version
Length
Ten paragraphs of three points each, roughly 1,300–1,500 words once written
Eight paragraphs, 890 words; about 1,510 in total with abstract, legends and 20 references
Repetition
Paragraphs 4, 5 and 6 each concluded that accuracy is similar
One parity paragraph for the two platform-neutral benchmarks; one for long tool chains, which asks a different question
The tool
Half a paragraph; the paper reads as a benchmark study
The agent interface is the subject of paragraph 2 and the benchmarks are its validation
Inspectability
Asserted, with “representative traces” as evidence
Paragraph 5 rests on counts: a history for every run, and how often agents wrote their own tools
User-defined tools
Not discussed
Stated openly: 70% of CompBioBench Galaxy runs used one, so the claim is about the workbench, not its installed tools
Error analysis
Run-to-run variation only
Adds the failure-cause audit: wrong answers come mostly from the task or from missing checks, not from failed execution
Token cost
1.53× presented as the result
1.53× is one model on one benchmark; the main runs sit between 1.0× and 4.2×, and both are reported
Numbers
AACR and dashboard values mixed
Each number tagged to a source; the conflicts are listed in the last section
Terms
“Unrestricted code”, “Galaxy-mediated execution”
“Galaxy” and “custom code”, the terms your repository fixes
Framing
Biomedical and cancer research
General computational biology; the ten IWC workflows are not cancer-specific
Numbers beyond the AACR abstract come from the lab’s public manuscript repository, read at its 5 November 2026 commit. It already holds a six-paragraph Brief Communication outline; this version follows its framing and terms, and departs from it on paragraph count, the user-defined-tool disclosure and the scoring conflict.
Format limits and word budget
A Brief Communication allows 1,200 words including abstract, references and figure legends, or 1,600 at the editor’s discretion. This plan totals about 1,510 words and so relies on that discretion.
Element
Journal limit
This plan
Abstract
70 words, unreferenced
64-word draft
Main text
Inside the 1,200 (1,600) total; no sections or subheadings
8 paragraphs, 890 words
Display items
2 figures or tables, 3 at discretion
2 figures of 3 panels each; legends 250 words
References
About 20 as a guideline
20, about 300 words
Online Methods
Required, with subheadings; outside the count
All implementation detail
Extended Data
Not mentioned in the guidelines
Allowed in practice: Multi-Embed carries eight Extended Data figures
Limits are from the Nature Methods content types page. It sets no word limit on titles.
Fit with the article type. The journal lists “software platforms” and practical improvements to existing tools as Brief Communication material. A comparison of established tools is an Analysis, at 3,000 words. Keep the agent interface as the subject, or an editor may redirect the paper.
Published examples run long. Two of your three model papers print at about 1,300 and 2,060 main-text words. The limit binds at submission; text grows in revision.
If the editor holds to 1,200 words, cut in this order:
1.  Fold paragraph 4 into one sentence of paragraph 3 (saves about 80).
2.  Move paragraph 7 to a Supplementary Note, leaving one sentence in paragraph 8 (saves about 85).
3.  Trim references to 15 (saves about 75).
4.  Trim legends to 180 words (saves about 70).
What the three model papers share
All three reach the method by paragraph five at the latest, then give every later paragraph one new angle with numbers. None repeats a finding to fill space.
Paper
Main text as published
Shape
What to borrow
Tangermeme (software toolkit)
14 paragraphs, about 2,060 words, 48 references, 2 figures
Need, gap, then design choices each justified, two demonstrations, what the tool is, outlook
Say why a design choice matters before showing it; close with a plain statement of what the tool is
Multi-Embed (learning framework)
About 10 paragraphs by your notes (paywalled; I read only the abstract), 2 figures, 8 Extended Data figures
Problem, method, successive validations each from a new angle, applications, limits
Each validation answers a different question; limits go in the last sentence
Continuous mass photometry (measurement method)
10 paragraphs, about 1,315 words, 19 references, 2 figures
Four short paragraphs narrowing to the gap, the idea in one sentence, then results
Opening paragraphs of 65–100 words; results stated as numbers against prior values
The moves they share, in order:
1.  Affirm, then turn. Each abstract opens with what the field can do and pivots on “yet”, “however” or “but” in the same sentence.
2.  Name the method in sentence two. Each second sentence starts “Here we” and names what is new.
3.  Narrow the gap in steps. Field, current approach, partial fixes, what is still missing. Each step is one short paragraph or less.
4.  Introduce the solution in one sentence that says what it is and why it differs from everything just described.
5.  One angle per paragraph. Open with the angle, give the setup in a clause, then numbers, then one sentence on what they mean.
6.  End on what it is, what it enables, and its limits. The two shorter papers have no separate discussion.
The third paper adds one lesson the first two do not: a Brief Communication can stay near 1,300 words and 19 references if implementation lives in Methods.
The argument
AI agents analyse biological data as accurately through Galaxy as with custom code, and every Galaxy run leaves a record a researcher can open and review. The paper is a tool report: the interface is the method and the paired comparison is its validation.
Claim
Evidence
Paragraph
State of the evidence
Agents can operate Galaxy on their own
The interface, and 1,920 completed Galaxy runs
2
In hand
Working through Galaxy costs no accuracy
Paired differences on 160 tasks, with intervals
3, 4
In hand; scoring release not frozen
Each run is reviewable
A history per run; share of runs with agent-written tools; one traced example
5
Counts exist; no rerun test yet
Checking, not execution, limits accuracy
Failure-cause audit and replicate agreement
6
BixBench only
The token cost can be engineered down
Token ratios in the main runs and after interface changes
7
Main runs in hand; early baseline unsourced
What the paper does not claim:
• That Galaxy beats custom code. The differences are small and the design tests parity.
• That it introduces a benchmark. Two of the three task sets are published by others.
• That analyses were reproduced. A recorded history is not a rerun; claim “rerunnable” only after rerunning a sample.
• That consensus improves accuracy. The gains are estimated from existing runs, and no voting step was executed.
Title options. “AI agents can perform accurate bioinformatics analyses through a computational workbench” is the candidate already in your repository. “Galaxy lets AI agents run accurate, inspectable bioinformatics analyses” names the tool, as tool papers in the journal usually do.
Paragraph outline
Eight paragraphs and 890 words. Each has a title stating its one message and three bullets saying how it is delivered. The titles are drafting labels and come out before submission. Numbers are from the committed results snapshot unless marked, and stay provisional until a release is frozen.
Abstract (70 words, three sentences)
• Affirm, then turn: agents can run bioinformatics analyses, but by writing custom code that is hard to inspect and reproduce.
• What we did: made Galaxy usable by agents and compared it with custom code on 160 tasks and 3,840 runs.
• Result and payoff: accuracy was similar, and every analysis left a record of tools, parameters and data.
Draft, 64 words:
AI agents can carry out bioinformatics analyses, but they do so by writing custom code that is hard to inspect and reproduce. Here we make the Galaxy workbench usable by agents and compare it with custom code across 160 tasks and 3,840 runs. Agents were similarly accurate through Galaxy, and every analysis left a record of tools, parameters and data that researchers can review.
P1. Agents can run whole analyses, but only as programmers
100 words. Job: affirmation, problem, gap.
• Affirmation: agents now plan and execute multi-omic, single-cell and machine-learning analyses, and benchmarks such as BixBench and CompBioBench measure how well.
• Problem: in every such benchmark the agent writes and runs its own code. The result is scripts, ad hoc environments and intermediate files that a reader must reconstruct to check an answer.
• Gap: workbenches such as Galaxy give people versioned tools, managed compute and recorded histories. Whether agents can work through one without losing accuracy has not been tested.
P2. An interface lets agents operate Galaxy, and we test it against custom code
130 words. Fig. 1a. Job: the solution in one sentence, why it differs, how it was tested.
• The tool: a Model Context Protocol server gives agents tool search, parameter descriptions, job submission and monitoring, and history inspection. Skills supply analysis know-how.
• Why it differs: agents keep the freedom to write code through user-defined tools, but every step runs as a Galaxy job and is recorded. Define “Galaxy” and “custom code” here, once.
• The test: four model configurations in one Codex harness, 160 tasks from three benchmarks, two conditions, three replicates, 3,840 runs.
P3. Accuracy is the same in Galaxy and custom code on platform-neutral tasks
120 words. Fig. 1b. Job: the central result.
• Angle: BixBench-Verified-50 and CompBioBench were written for code-writing agents, so they give Galaxy no home advantage.
• Numbers: BixBench 89.5% against 88.3% (537 and 530 of 600 runs). CompBioBench 87.0 against 86.8 mean score. Give each difference with a 95% interval from task-level pairing.
• Reading: no model pays a penalty. The largest per-model gap is 3.3 points, in Galaxy’s favour. The result holds under the raw BixBench key (87.2% against 86.8%) as well as the reviewed one.
P4. On long tool chains, Galaxy holds or leads
110 words. Fig. 1c. Job: a different question from P3, namely whether parity survives many chained tools.
• Angle: ten tasks derived from IWC workflows, whose reference workflows run 2 to 27 tool steps, scored by agreement of final outputs with the reference.
• Numbers: mean output agreement 0.990 in Galaxy against 0.953 with custom code. Five tasks are at ceiling in both; three carry the gap (amplicon denoising, mitogenome assembly, single-cell pseudobulk).
• Reading: these tasks originate in Galaxy, so conclude “no penalty as tool chains lengthen”, not “Galaxy wins on hard tasks”. Ten tasks cannot support the second.
P5. Every Galaxy run leaves a record a researcher can open
120 words. Fig. 2a. Job: the differentiator, with counts.
• What is recorded: tool identity and version, requested and resolved parameters, input and output datasets, and job states, viewable in the standard Galaxy interface without spending tokens.
• Counts: all 1,200 CompBioBench Galaxy runs have a public history. Agents used a user-defined tool in 70% of them and installed tools alone in 29%, so the record covers agent-written steps too.
• Traced example: bix-45-q1 failed in all 12 Galaxy runs under the original key. The recorded tool version shows why: Galaxy’s PhyKIT differs from the one behind the accepted answer. Both values are now accepted.
P6. Checking, not execution, limits accuracy
130 words. Fig. 2b. Job: the unexpected finding, and the honest reading of consensus.
• Errors are systematic: on BixBench three tasks account for 71 of the 133 incorrect runs and fail in both conditions. The trace audit attributes most incorrect runs to under-specified tasks or answer keys.
• Agents recover but do not verify: most correct runs hit at least one failed step and recovered. Missing validation of the final answer is the main agent-side cause of error.
• Repeats help little: on BixBench a majority of three adds 0.5 points in Galaxy and 2.2 with custom code. At least one replicate is correct in 92–93% of cases, but choosing it needs the answer, so it is a ceiling and not a method.
P7. The token cost comes from the interface and can be engineered down
110 words. Fig. 2c. Job: practicality.
• Cost in the main runs: Galaxy used 4.2× the tokens of custom code on BixBench, 2.5× on CompBioBench and about the same as custom code on IWC (0.96×).
• Where it went and how it fell: cached context re-read over more steps, not reasoning. Shorter replies, parameter templates and longer waits took one model on BixBench from 3.45× to 1.53×, with 137 of 150 runs correct.
• Framing: agents act as virtual users whose traces show where software is hard to use. Say accuracy was retained, not unchanged.
P8. What the tool is, what it enables, and its limits
70 words. Job: close as the model papers do.
• What it is: one sentence. An interface through which agents analyse data in Galaxy as accurately as with custom code, leaving a reviewable record.
• What it enables: review in a familiar interface, continuing an analysis without tokens, and cheap cross-method checks. Offer the last as an untested hypothesis.
• Limits: four model configurations, one harness, prompts that differ between conditions, and models that change quickly.
Display items
Two figures of three panels each: Figure 1 proves parity and Figure 2 shows what Galaxy adds and what it costs. Six panels fit a 250-word legend budget; eight do not.
Figure
Panel
Shows
Supports
1. Design and accuracy
a
Study design: one model configuration, two conditions, and the interface between agent and Galaxy
P2
1
b
Galaxy minus custom code, per benchmark, with 95% intervals; one point per model and one pooled
P3
1
c
IWC output agreement per task in both conditions, ordered by number of tool steps
P4
2. Record, errors and cost
a
One Galaxy history, annotated: an installed tool, a user-defined tool, a failed job and its recovery
P5
2
b
Incorrect BixBench runs by cause, split by how many sibling replicates were correct
P6
2
c
Galaxy tokens relative to custom code: three benchmarks in the main runs, then the BixBench stages down to 1.53×
P7
Panel 1b should plot the difference, not two bars side by side. The claim is about the gap and its interval, and bars at 87–90% hide both.
Extended Data or Supplementary Information takes the rest: per-model accuracy, raw against reviewed scoring, the consensus table, user-defined-tool use by benchmark, the IWC multi-step tasks and the main-run token totals. A table of benchmark materials, prompts, code and traces is the natural third display item if the editor allows one.
Settle before drafting
The AACR abstract, the results snapshot and the repository outline give different values for most headline numbers. The parity conclusion survives every version, but the paper needs one frozen release. Each pair is Galaxy, then custom code.
Number
AACR abstract
Results snapshot, deployed 28 Oct 2026
Repository outline
Reading
BixBench accuracy
87.7%, 87.2%
Reviewed key 89.5%, 88.3%; raw key 87.2%, 86.8%
87.7%, 87.2%
Three scorings. Review moved a net 14 Galaxy and 9 custom-code runs to pass; bix-45-q1 alone moved 12 and 4. Report raw and reviewed.
CompBioBench score
87.0, 86.7
87.0, 86.75
87.0, 86.7
Rounding only. Fix one rule.
IWC, runs at 0.99 agreement or above
80.0%, 74.2%
79.2%, 72.5% (95 and 87 of 120)
83.3%, 80.0%
Three values. Lead with mean agreement, 0.990 and 0.953, and define one threshold.
Gain from a majority of three
Up to 2.2 points
BixBench: 0.5, 2.2
0 to 2.3
Depends on the scoring above.
Incorrect BixBench runs in the cause audit
Not given
133
151
The audit predates the reviewed key. Rerun it.
Optimized Galaxy tokens and accuracy
20× down to 1.5×, no loss
3.45× down to 1.53×; 139 then 137 of 150 correct
About 20× baseline from one run per task; 136 then 137 of 150
Baseline is not on the results site. Say “retained”.
I recomputed the snapshot column from the results files committed under data/site/ in the repository. The other two columns are quoted as written.
Work that would most strengthen the submission:
[ ] Freeze one results release and regenerate every number in the text from it.
[ ] State an equivalence margin before computing intervals, and pair by task.
[ ] Report both BixBench scorings. Reviewers will ask whether answer-key review favoured Galaxy.
[ ] Report user-defined-tool use for all three benchmarks, and say what the record keeps for such a tool (script, environment, inputs).
[ ] Decide whether “rerunnable” is claimed. If so, rerun a sample of histories and report how many reproduce the answer.
[ ] Extend the failure-cause audit to CompBioBench, or limit P6 to BixBench.
[ ] Decide whether the IWC multi-step tasks enter. Galaxy leads 67% to 59%, but one imaging task carries most of the gap and 16 of 180 runs are flagged as trial runs.
[ ] Disclose in Methods that prompts differ between conditions (707 against 366 median words on BixBench, per the repository outline).
[ ] Drop the AACR line that IWC needs cancer knowledge; the ten workflows cover QC, RNA-seq, ATAC-seq, assembly, amplicon and proteomics.
[ ] Send a presubmission enquiry asking the editor to confirm Brief Communication over Analysis, and the 1,600-word ceiling.
Sources
• Nature Methods content types: Brief Communication limits.
• Tangermeme, Multi-Embed and Continuous mass photometry: the three model papers. Paragraph and word counts are mine, from the published pages.
• goeckslab/agent-galaxy-benchmark-manuscript: outlines, token tables and the committed copy of the results site, at the commit of 5 November 2026.
• Your AACR abstract and paragraph notes, as supplied.
