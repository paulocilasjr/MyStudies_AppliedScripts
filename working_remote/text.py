Written for: AACR 2027 abstract reviewers. The checks are for you.

Most numbers in this version match the results tables exactly. Three need correcting, one claim needs a qualifier, and two details only you can confirm. With the fixes below the abstract is 2,576 characters excluding spaces, still under 2,600.

Your three items

Same TCGA subset: correct. All three strategies used the same frozen patient split (the core design specifies "same eligible TCGA" for the federated arm). The TCGA-only model differs in two other ways, though; see the qualifier below.
Seed range and baseline: both correct.
0.340–0.439 is the mean of each pretraining seed after averaging its three fine-tuning seeds.
The 0.368 baseline is weighted the same way as the model results: each of the eight cohorts counts equally.
AI statements: possibly incomplete. The repo has a Codex (OpenAI) skill set up to implement the project, and the reports review a Codex-written summary of the Oct 13 results. If Codex wrote any training or analysis code, the Methods sentence should name it, for example "(Codex, OpenAI; Claude, Anthropic)". Confirm this with your coauthors.
Corrections

Abstract says	Should say	Why
"a spread 7.6 times"	7.8	The exact values give 0.0989 / 0.0126 = 7.84. The 7.6 came from dividing rounded numbers (0.099 / 0.013).
"0.018 below released COMPASS"	0.019	0.4574 − 0.4388 = 0.0185, which rounds to 0.019.
"equal sample exposures"	"equal total sample exposures"	All 15 runs had 2,764,800 total samples, but the tumor share was not equal (next row).
"The TCGA-only model reached 0.412/0.412 …, so tumor–normal pretraining showed no mean AUPRC gain"	Add "with 3.4-fold more tumor exposures"	Samples were drawn uniformly across rows, so GTEx made up about 70% of what the pooled and federated models saw. With 8,210 tumors, the TCGA-only model saw 3.4× more tumor samples. Without saying so, the no-gain claim reads as a pure test of adding normal tissue, which it isn't.
"released COMPASS …, pretrained on more tumors"	"which used a different recipe and more tumors"	As written, tumor count reads as the cause of the gap. The released checkpoint also differs in recipe; for example, it used hard negatives.
The TCGA-only model also used its own TCGA-only scaler, while the pooled and federated models shared one. Your design notes say this must be reported. There's no room for it in the abstract, but have it ready for questions.

What I can't check from the repo

8,210 TCGA tumors. This number appears nowhere in the repo. If it came from section 1 of the HPC command output (the experiment 11 dataset), it's correct. It is 1,974 fewer patients than the paper's 10,184, so expect the question.
Check tcga_stage_count_deviation_from_compass.json to see which filtering stage lost them.
Check whether all 33 cancer types survived. If they did, adding back "(33 cancer types)" costs about 15 characters and still fits.
19,616 GTEx samples. This is correct if the same manifest lists it and exclude_cell_derived is false.
Corrected abstract (2,576 characters excluding whitespace)

Federated pretraining of a tumor–normal transcriptomic foundation model achieves immunotherapy response prediction comparable to centralized training

Purpose: Transcriptomic foundation models (FMs) such as COMPASS can predict immune checkpoint inhibitor (ICI) response, but centralized pretraining requires pooling transcriptomes that institutions often cannot share. We assessed whether federated pretraining, which exchanges only model updates, preserves downstream ICI prediction when client datasets differ in source and tissue state, and how much pretraining seed affects such comparisons.

Methods: We pretrained the COMPASS concept-bottleneck transformer from scratch (self-supervised triplet objective) by FedAvg across two simulated clients holding 8,210 TCGA tumors or 19,616 GTEx normal samples, harmonized to 15,672 genes [log2(TPM+1)]. Centralized comparators used pooled TCGA+GTEx or the same TCGA subset alone (five pretraining seeds per strategy; equal total sample exposures). With each encoder frozen, we trained the head alone or the projector plus head (three fine-tuning seeds) by nested leave-one-cohort-out validation across eight public ICI cohorts (346 patients, 113 responders; seven adaptation cohorts per fold). The released COMPASS checkpoint, pretrained on 10,184 TCGA tumors, was adapted identically. Paired 95% CIs used a cohort-and-patient bootstrap. Analysis code was AI-assisted (Claude, Anthropic) and author-verified.

Results: Federated and pooled models reached nearly identical mean held-out AUPRC (head-only/projector+head: 0.400/0.402 vs. 0.400/0.401; paired differences −0.0005/+0.001, CI bounds within ±0.046; no-skill baseline, 0.368). The TCGA-only model, with 3.4-fold more tumor exposures, reached 0.412/0.412 (federated differences −0.013/−0.010, CI bounds within ±0.067), so tumor–normal pretraining showed no mean AUPRC gain. All from-scratch models trailed released COMPASS (0.457/0.443), which used a different recipe and more tumors. Federated validation triplet loss exceeded pooled loss (context-averaged, 0.400 ± 0.058 vs. 0.231 ± 0.042) despite similar downstream AUPRC. Across pretraining seeds, federated head-only AUPRC ranged from 0.340 (below no-skill) to 0.439 (0.019 below released COMPASS), a spread 7.8 times the largest mean difference among from-scratch strategies.

Conclusions: In a two-client simulation, federated tumor–normal pretraining yielded mean ICI prediction similar to centralized training on the same data, without exchanging patient-level transcriptomes. Higher pretraining loss did not correspond to lower downstream AUPRC, and seed variability exceeded mean differences among the evaluated strategies. These findings support multi-seed, no-skill-referenced FM benchmarking and motivate real-world multisite validation with formal privacy assessment.

Generative AI (Claude, Anthropic) assisted with drafting and editing this abstract; the authors verified all results.

The "3.4-fold" assumes 8,210 TCGA tumors. If the manifest gives a different TCGA count, send it to me and I'll recompute that number.
