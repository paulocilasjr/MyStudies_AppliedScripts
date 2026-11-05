Here is the final version. It comes to 2,523 characters excluding whitespace, with the title and both AI statements included, which leaves about 75 characters of margin. Enter the author and affiliation lines in the portal’s author fields, not in the abstract body.

Federated pretraining of a tumor–normal transcriptomic foundation model achieves immunotherapy response prediction comparable to centralized training

Purpose: Transcriptomic foundation models (FMs) such as COMPASS can predict immune checkpoint inhibitor (ICI) response, but centralized pretraining requires pooling transcriptomes that institutions often cannot share. We assessed whether federated pretraining, which exchanges only model updates, preserves downstream ICI prediction when client datasets differ in source and tissue state, and how much pretraining seed affects such comparisons.

Methods: We pretrained the COMPASS concept-bottleneck transformer from scratch (self-supervised triplet objective) by FedAvg across two simulated clients holding 8,210 TCGA tumors or 19,616 GTEx normal samples, harmonized to 15,672 genes [log2(TPM+1)]. Centralized comparators used pooled TCGA+GTEx or the same TCGA subset alone (five pretraining seeds per strategy; equal sample exposures). With each encoder frozen, we trained the head alone or the projector plus head (three fine-tuning seeds) by nested leave-one-cohort-out validation across eight public ICI cohorts (346 patients, 113 responders; seven adaptation cohorts per fold). The released COMPASS checkpoint, pretrained on 10,184 TCGA tumors, was adapted identically. Paired 95% CIs used a cohort-and-patient bootstrap. Analysis code was AI-assisted (Claude, Anthropic) and author-verified.

Results: Federated and pooled models reached nearly identical mean held-out AUPRC (head-only/projector+head: 0.400/0.402 vs. 0.400/0.401; paired differences −0.0005/+0.001, CI bounds within ±0.046; no-skill baseline, 0.368). The TCGA-only model reached 0.412/0.412 (federated differences −0.013/−0.010, CI bounds within ±0.067), so tumor–normal pretraining showed no mean AUPRC gain. All from-scratch models trailed released COMPASS (0.457/0.443), pretrained on more tumors. Federated validation triplet loss exceeded pooled loss (context-averaged, 0.400 ± 0.058 vs. 0.231 ± 0.042) despite similar downstream AUPRC. Across pretraining seeds, federated head-only AUPRC ranged from 0.340 (below no-skill) to 0.439 (0.018 below released COMPASS), a spread 7.6 times the largest mean difference among from-scratch strategies.

Conclusions: In a two-client simulation, federated tumor–normal pretraining yielded mean ICI prediction similar to centralized training on the same data, without exchanging patient-level transcriptomes. Higher pretraining loss did not correspond to lower downstream AUPRC, and seed variability exceeded mean differences among the evaluated strategies. These findings support multi-seed, no-skill-referenced FM benchmarking and motivate real-world multisite validation with formal privacy assessment.

Generative AI (Claude, Anthropic) assisted with drafting and editing this abstract; the authors verified all results.

I adopted all of the reviewer’s scientific corrections, with four departures:

Title grammar. I kept my fix (“prediction comparable to”). The reviewer’s wording (“comparable … prediction to”) splits the comparison.
“One GTEx context.” I dropped it. It is jargon that most readers can’t decode.
Best-seed result. I kept “0.018 below released COMPASS” rather than “near,” because the exact gap is more memorable.
Normal-tissue result. I kept “tumor–normal pretraining showed no mean AUPRC gain” as an explicit statement. It is one of your three findings, and the reviewer’s version had left it implicit.

Three things to confirm before submitting:

Same TCGA subset. The text now says the TCGA-only comparator used “the same TCGA subset.” Confirm it used exactly the same 8,210 tumors as the federated model.
Seed range and baseline. Confirm that 0.340–0.439 is the per-pretraining-seed mean after averaging the three fine-tuning seeds, and that the 0.368 baseline uses the same cohort weighting as the model results.
AI statements. Confirm that all coauthors agree with both statements.
