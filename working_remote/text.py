The federated model's best result came from pretraining seed 17. Averaged over its three prediction heads, it reached AUPRC 0.439 and AUROC 0.596 with head-only fine-tuning. Across the five pretraining seeds, AUPRC had a standard deviation of 0.038 (variance 0.0014) and AUROC a standard deviation of 0.053 (variance 0.0028).

These numbers come from the core run's per-fit file, macro_metrics_by_seed.tsv. It reproduces the family means exactly (0.4123, 0.4001, 0.3996, and 0.4574 for published COMPASS), so it's the right source.

Federated model, head-only fine-tuning (each seed is the mean of 3 heads)

Pretraining seed	AUPRC	AUROC
17 (best)	0.439	0.596
64	0.424	0.566
42	0.404	0.530
91	0.392	0.526
24 (worst)	0.340	0.454
Mean	0.400	0.534
SD across seeds	0.038	0.053
Variance across seeds	0.0014	0.0028
Published COMPASS (reference)	0.457	0.584
No-skill baseline	0.368	0.500
Best single fit (one seed, one head): AUPRC 0.465 (seed 42 with fine-tuning seed 42) and AUROC 0.598 (seed 17). Across all 15 fits, the SD is 0.045 for AUPRC and 0.054 for AUROC.
Worst seed: seed 24 is below no-skill on both metrics (AUROC 0.454 is below 0.5). Its three heads all landed between 0.335 and 0.344, so the problem is the pretrained encoder, not head noise.
Projector-plus-head fine-tuning: the best seed was seed 42 (AUPRC 0.425) and seed 17 had the best AUROC (0.574). The best single fit reached AUPRC 0.467 and AUROC 0.593. Across seeds, the SD was 0.036 for AUPRC and 0.046 for AUROC, and seed 24 was again worst (0.339 and 0.460).
Compared with the other two strategies (SD across the 5 seeds, head-only)

TCGA-only	Pooled	Federated
AUPRC SD	0.035	0.028	0.038
AUROC SD	0.040	0.039	0.053
Best seed AUPRC	0.464 (seed 42)	0.447 (seed 17)	0.439 (seed 17)
Federated looks somewhat more sensitive to the seed. But with only 5 seeds per strategy, a variance ratio this size (about 1.8×) happens often by chance, so I wouldn't claim it.

A pattern worth noticing

Pooled and federated training rank the seeds almost identically: seed 17 is best and seed 24 worst in both. The rank correlation of the seed means is 0.9 (Spearman, n = 5; p ≈ 0.08, so suggestive only). Each pretraining seed seems to set roughly how good the encoder will be, and federation keeps that ranking. This fits the CKA result, where matching seeds made federated and pooled encoders more similar (0.71 vs 0.61 for different seeds).

Don't headline the best seed or best fit in the abstract. The 0.465 single fit is higher than COMPASS's 0.457, but choosing the best of 15 fits after the fact is exactly the seed-selection problem the abstract warns about. COMPASS's 0.457 is an average of 3 heads, so the fair comparison is the 5-seed mean (0.400). The abstract already reports the seed range (0.340 to 0.439), which makes the same point honestly.
