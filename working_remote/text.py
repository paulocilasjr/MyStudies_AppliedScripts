I checked all four against the code and the results. One needs a real number filled in, two are right as written, and one word shouldn't be used.

1. [R] and [E]: 100 rounds, 1 local epoch per round. The core finalizer (finalize_foundation.py:64-73) requires all of the following for every federated run:

exactly 100 rounds, kept to the final round with no early stopping;
one local epoch per round;
weights proportional to each site's training sample count, so about 30% TCGA and 70% GTEx;
Adam state reset every round.
Watch the word "epoch." In this code a local epoch is a fixed budget, not a full pass over the site's data. Each site processes 13,824 samples per round (half of 27,648), which is 108 optimizer steps of 128. For the TCGA site that is about 1.7 passes per round; for the GTEx site about 0.7. A federated-learning reviewer will read "local epoch" as one full pass, so this wording is safer: "FedAvg, 100 rounds of 108 local steps per site, sample-count weights."

2. Site partition: correct, keep "partitioned by source." The two clients are literally named TCGA and GTEx, and the aggregation weights are keyed by those names. One site holds all the TCGA tumors and the other all the GTEx normal tissue; it is not a random split.

3. CKA and Spearman wording: the reading is correct, but it is the most favorable comparison. E10 compares federated vs pooled encoders trained from the same seed against pooled vs pooled pairs, which necessarily use different seeds (e10_biological_agreement.py:80-85). A shared seed means shared initialization, which makes the federated pair look closer. The like-for-like comparison is less flattering:

Comparison	CKA in ICB cohorts	CKA in TCGA	Concept-importance Spearman
Pooled vs pooled (different seeds)	0.743	0.657	0.534
Federated vs pooled, same seed	0.707	0.672	0.573
Federated vs pooled, different seeds	0.614	0.557	0.470
Federated vs federated (different seeds)	0.632	0.627	0.495
With different seeds, federated−pooled similarity is lower than pooled−pooled. The gap's 95% CI excludes zero: −0.129 in ICB cohorts and −0.100 in TCGA. So federation keeps most of what the seed determines but adds some variation of its own, which matches its larger seed spread in loss and AUPRC.

The Results sentence is accurate as long as it says "same-seed." But "matched centralized pretraining in … representations" in the Conclusions overstates it. I'd change the Conclusions to: "Federated pretraining matched centralized pretraining in prediction and stayed close to it in representations and response-relevant biology, without exchanging transcriptomes."

4. "Prespecified": leave it out. Neither condition for using it holds:

The margin was first written into the experiment config on 2026-11-05 (commit e11b360). The federated−pooled results it is applied to were committed on 2026-10-28, and the federated−pooled difference was already known before that.
The original analysis plan (compass_iteration_20261009.json:114-115) set noninferiority_margin: null with equivalence testing disabled.
What you can truthfully say is that the margin is derived only from published COMPASS results and the no-skill floor, never from our model scores. The current wording, "a margin from published results only," already says exactly that.
