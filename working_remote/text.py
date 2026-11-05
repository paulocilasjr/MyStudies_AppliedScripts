Written for: AACR 2027 abstract reviewers and the committee that picks oral presentations (category BCS02, "Foundation and multimodal models").

The full abstract is 2,584 characters without spaces (title, sections and AI sentence), under the 2,600 limit. Every number in it matches the tracked results tables.

Federated pretraining of a transcriptomic foundation model across tumor and normal sites predicts immunotherapy response comparably to centralized training

Purpose: Transcriptomic foundation models (FMs) such as COMPASS predict response to immune checkpoint inhibitors (ICIs), but scaling them requires patient transcriptomes that cancer centers often cannot share. Federated learning exchanges only model updates. We asked whether federated pretraining preserves ICI response prediction under strong between-site heterogeneity, and how pretraining strategies should be compared.

Methods: We pretrained the COMPASS concept-bottleneck transformer from scratch with its self-supervised triplet objective by FedAvg across two simulated sites: TCGA tumors (10,184; 33 cancer types) and GTEx normal tissues (19,616), which differ in both data source and tissue state. Both used the same 15,672-gene log2(TPM+1) input. Comparators were centralized FMs pretrained on pooled data and on TCGA alone (five seeds per strategy, identical sample budgets). Each frozen encoder was fine-tuned (head-only or projector+head; three fine-tuning seeds) by nested leave-one-cohort-out validation across eight public ICI cohorts (346 patients, 113 responders; seven adaptation cohorts per fold vs. 15 in the COMPASS study). The released COMPASS checkpoint, fine-tuned identically, served as reference. CIs used a cohort-and-patient bootstrap.

Results: Federated and pooled FMs reached nearly identical mean held-out AUPRC (head-only/projector+head: 0.400/0.402 vs. 0.400/0.401; paired difference −0.0005/+0.001, 95% CIs within ±0.046; no-skill baseline, 0.368). Adding normal tissue did not improve transfer: the TCGA-only FM reached 0.412/0.412, and the federated FM trailed it by 0.013/0.010 (CIs within ±0.067). All from-scratch FMs, centralized or federated, trailed the released checkpoint (0.457/0.443). Two findings bear on FM evaluation. First, federated pretraining ended with 1.7-fold higher context-averaged validation triplet loss than pooled training (0.400 ± 0.058 vs. 0.231 ± 0.042), yet ICI performance was not lower. Second, pretraining seed alone moved federated head-only AUPRC from 0.340 (below no-skill) to 0.439 (near the released checkpoint), a spread nearly eight times the largest between-strategy difference.

Conclusions: Federated pretraining across sites differing in source and tissue state was comparable to centralized training for ICI response prediction, without pooling transcriptomes. Pretraining loss and single-seed comparisons misled: one seed could place a model below chance or near the reference. Oncology FM benchmarks should report multi-seed downstream performance against a no-skill baseline. This supports multi-institution deployment with formal privacy evaluation, letting cancer centers jointly train FMs on data they cannot share.

Generative AI (Claude, Anthropic) assisted with drafting, editing and analysis code; the authors verified all results.

What changed and why

The seed finding is now the headline result. The worst federated pretraining seed (0.340) scored below the no-skill baseline (0.368), and the best (0.439) came within 0.018 of released COMPASS. That gives the committee one concrete, surprising observation instead of an abstract claim about variance.
The no-skill baseline is 0.368, not the 0.336 responder rate. It is calculated with the same AUPRC formula the results use. Reporting it openly is better than having a reviewer find it.
The gap to released COMPASS no longer blames anything. The CIs for that gap include zero, and the TCGA-only centralized model trails too. So the abstract states the gap without implying federation caused it.
Fixed from the comments:
The 1.7-fold loss ratio is specified as context-averaged; averaged per sample, the ratio is only 1.44.
"Matched budgets" now reads "identical sample budgets"; all 15 runs used 2,764,800 samples.
FedAvg and three fine-tuning seeds are named.
The bootstrap method is stated.
The AI sentence covers how it was actually used.
Before you submit

Confirm the two dataset counts on the HPC. 10,184 is the COMPASS paper's TCGA count, and 19,616 is the full GTEx source matrix; neither is confirmed as the number used in training. Run this and replace them:
Numbers of similar length keep you under the limit.
Confirm the AI sentence with your coauthors. I wrote it from this session; adjust it if the analysis code was produced another way.
If the portal counts more strictly (for example, section labels), cut "Two findings bear on FM evaluation." That saves 29 characters.
