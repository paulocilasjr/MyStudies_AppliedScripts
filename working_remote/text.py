Here is the final abstract. It combines my earlier review with the reviewer comments you attached. It uses only the results you already have, with no new claims. The title, body and AI disclosure come to about 2,500 of the 2,600 allowed characters (spaces excluded), leaving roughly 100 characters for one optional insertion described below.

Federated tumor–normal pretraining of a transcriptomic foundation model achieves immunotherapy response prediction comparable to centralized training

Purpose: Transcriptomic foundation models (FMs) such as COMPASS can predict response to immune checkpoint inhibitors (ICIs), but scaling them beyond public data would require pooling patient transcriptomes that cancer centers often cannot share. Federated learning keeps data at each site and exchanges only model updates. We asked whether federated pretraining preserves an FM’s transfer to ICI response prediction in a strongly heterogeneous two-site simulation.

Methods: We pretrained the COMPASS concept-bottleneck transformer from random initialization by self-supervised federated learning across two simulated clients: one held TCGA tumors (10,184; 33 cancer types) and the other GTEx normal tissues (19,616), so the sites differed in both data source and tissue state. Both were harmonized to the same 15,672-gene log2(TPM+1) input. Comparators were centralized FMs pretrained on the pooled data and on TCGA alone (five seeds per strategy, matched training budgets). Each frozen encoder was fine-tuned (head-only or projector+head) by nested leave-one-cohort-out validation across eight public ICI cohorts (346 patients, 113 responders; seven adaptation cohorts per fold vs. 15 in the original COMPASS study). The released COMPASS checkpoint, fine-tuned identically, served as reference.

Results: Federated and centralized pooled FMs reached nearly identical mean held-out AUPRC (head-only/projector+head: 0.400/0.402 vs. 0.400/0.401; paired difference −0.0005/+0.001; bootstrap 95% CIs within ±0.046). Adding normal tissue did not improve transfer: the TCGA-only FM reached 0.412/0.412, and the federated FM trailed it by 0.013/0.010 (CIs within ±0.067). The released COMPASS checkpoint reached 0.457/0.443. Two findings bear on how FMs should be compared. Federated pretraining ended with 1.7-fold higher validation triplet loss than pooled training (0.400 ± 0.058 vs. 0.231 ± 0.042), yet ICI performance was not lower. Pretraining seed moved federated head-only AUPRC from 0.340 to 0.439, a spread more than seven times larger than any difference between our pretraining strategies.

Conclusions: Federated pretraining across two sites whose data differed in both source and tissue state yielded an FM with ICI response prediction comparable to centralized training, without moving any transcriptome between sites. Pretraining loss and single-seed comparisons were unreliable guides to clinical transfer, so FM benchmarks for oncology endpoints should use multi-seed downstream evaluation. These results motivate real multi-institution deployment with formal privacy evaluation, which would let cancer centers jointly train FMs on data they cannot share.

Generative AI (Claude, Anthropic) was used to edit the language of this abstract.

Why it is built this way

The abstract now makes two arguments instead of one. The first is the feasibility result: federation matches centralized training. On its own, that reads as an engineering check, which both reviews flagged as the main obstacle to getting a talk.

The second is a methodological lesson that matters to anyone building or benchmarking oncology foundation models. Pretraining loss misled, and seed variance swamped every between-strategy difference. That second finding is what widens the audience. It also fits the program, which includes a forum on building the AI evaluation infrastructure that will drive innovative treatments. 
aacr

The tumor/normal client split is now framed as a stress test, stated factually. The reviewer’s main objection, that client identity, data source and tissue state are perfectly aligned, becomes the reason the result is interesting.

I made three deliberate changes from the attached reviewer’s version:

Title verb. I used “comparable” rather than “approaches.” The point estimates are essentially identical, so “approaches” undersells the result. “Comparable” still avoids an equivalence claim.
Abbreviations. I dropped LFT/PFT entirely in favor of plain “head-only/projector+head.” This avoids defining abbreviations for a broad audience. It also avoids the reviewer’s expansion “linear-probe fine-tuning,” which may not match what COMPASS calls these modes.
Released COMPASS result. I kept it visible, as both reviews asked, but stated it without editorializing.

Category: I confirmed the reviewer’s recommendation in the official call. BCS02 (Artificial Intelligence, Machine Learning, and Data Science) lists “Foundation and multimodal models” and “Clinical AI for cancer prediction and precision oncology” as subclassifications. Choose “Foundation and multimodal models.” 
aacr

Before you submit (deadline: Nov 10, 11:59 p.m. ET)

Optional insertion. If you can compute it, the most valuable addition is the mean cohort-specific no-skill AUPRC. Insert it after the first Results parenthesis as “(no-skill baseline, 0.XX).” Without it, readers can’t tell how far 0.40 sits above chance. It fits in the remaining space. If you would rather name the federated algorithm (e.g., “FedAvg”), that also fits, but not both alongside exact CI endpoints.

Facts to verify:

GTEx count. The reviewer noticed that 19,616 differs from the 17,382 samples in your earlier project plan. Confirm the final number.
Seed range. Confirm that 0.340–0.439 reflects pretraining seeds rather than fine-tuning randomness.
“Matched training budgets.” Confirm this describes what was actually matched.
Differences of 0.013/0.010. Confirm these are your computed paired differences (simple subtraction of the means gives 0.012/0.010).
AI disclosure. Adjust the sentence to reflect how AI was actually used in the final text.

Coauthor accounts. This year all coauthors need a verified myAACR account before they can be added to a submission. Ask all five coauthors to do this today rather than on deadline night. 
aacr

What the wording can’t change

The abstract now presents everything the data support, and that maximizes its standing. Selection for a talk will still depend on the content. The two things that would move it most remain a real Moffitt–OHSU federated run and evidence that normal tissue changes what the model learns. Neither is likely by November 10.

If either comes through by early January, it would be the basis for a stronger manuscript or talk. Have the per-cohort AUPRCs and paired seed differences ready either way. They are the first slides a minisymposium audience will ask for.
