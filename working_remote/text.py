Answers below, all for head-only fine-tuning, the primary analysis.

1. Equivalence margin: ±0.078 AUPRC

How it's derived: it is half of published COMPASS's reported gain over no-skill on these eight cohorts: 0.5 × (0.525 − 0.3685) = 0.078. It uses only published numbers, not our model scores. The 0.525 is the AUPRC published for COMPASS, not the 0.457 we measured when re-running it.
Why half: this follows the usual non-inferiority convention of keeping at least 50% of the reference model's effect.
Result: the federated−pooled 90% CI was −0.036 to 0.033 when resampling cohorts and patients, and −0.026 to 0.025 when resampling patients only. Both sit inside ±0.078 and also inside the stricter ±0.039 (a quarter of COMPASS's gain).
Projector-plus-head fine-tuning: the margin is ±0.075, and the CI of −0.036 to 0.039 is equivalent at that margin. At the stricter ±0.038 the result is "non-inferior, not equivalent".
2. TCGA-only AUPRC: 0.412

AUROC: 0.561.
Across the 5 pretraining seeds: AUPRC ranged from 0.371 to 0.464 (SD 0.035). The best was seed 42 at 0.464.
Projector-plus-head fine-tuning: 0.412 (AUROC 0.562).
3. Federated vs untrained encoder: difference +0.005 AUPRC (0.400 vs 0.395)

How uncertainty was estimated	95% CI
Resampling cohorts and patients	−0.043 to 0.055
Resampling patients within fixed cohorts	−0.030 to 0.039
Across the 5 pretraining seeds (t-interval)	−0.052 to 0.062
The exact sign-flip test across seeds gives p = 0.875. Every interval includes zero, so the federated model can't be distinguished from the untrained encoder; the same holds for pooled and TCGA-only.
