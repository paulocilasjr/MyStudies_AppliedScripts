Written for: you, plus one optional sentence at the end for AACR reviewers.

The federated model's pretraining loss was higher than pooled training at all five seeds (0.400 vs 0.231), yet its ICB prediction was equivalent. Pretraining loss didn't predict ICB performance in any strategy.

The loss is the validation loss of the pretraining task (recognizing a perturbed copy of each sample among other samples of the same tissue), measured on held-out pretraining samples at the checkpoint each run kept. Lower is better. The numbers come from foundation_summary.tsv, and I report it two ways:

Context-averaged: each of the 34 contexts (33 tumor types plus one normal-tissue context) counts equally, so tumors dominate. This is the number the abstract reports and the one used to pick checkpoints.
Sample-averaged: every sample counts equally, so GTEx normal tissue dominates, since it is about 70% of the samples.
Context-averaged validation loss by pretraining seed

Seed	TCGA-only	Pooled	Federated	Federated − pooled
17	0.180	0.220	0.434	+0.215
24	0.157	0.183	0.468	+0.284
42	0.247	0.299	0.323	+0.024
64	0.141	0.233	0.413	+0.180
91	0.203	0.222	0.361	+0.139
Mean (SD)	0.186 (0.042)	0.231 (0.042)	0.400 (0.058)	+0.168
Sample-averaged mean	0.178	0.136	0.196	+0.060
What the losses show

Federated pretraining fits the pretraining task less well, at every seed. The gap ranges from nearly nothing (seed 42, +0.024) to +0.284 (seed 24). Federated loss also varies more from seed to seed (SD 0.058 vs 0.042).
The shortfall is mostly on tumors. The gap is almost three times larger when contexts count equally (+0.168) than when samples count equally (+0.060).
A likely explanation (my hypothesis, not tested): with weights set by sample count, FedAvg gives the GTEx site about 70% of every update (19,616 of 27,826 samples). Each site also trains only on its own data between averaging rounds, so the tumor site's progress gets diluted. Pooled training mixes both kinds of samples in every step.
E08B tests this directly: it compares FedAvg with FedProx, SCAFFOLD and FedAdam, which are designed to correct this drift.
Lower loss did not mean better ICB prediction.
Within each strategy, the rank correlation between loss and AUPRC was between −0.10 and +0.40 across the 5 seeds. Across all 10 pooled and federated encoders it was +0.08, which is essentially zero.
In the federated model, seed 42 had the lowest loss (0.323) but only middling AUPRC (0.404). Seed 17 had a high loss (0.434) yet the best AUPRC (0.439).
Seed 24 is the only seed that was worst on both.
The TCGA-only loss isn't directly comparable. That model never saw normal tissue, so it was validated on tumor samples only (33 contexts). Its lower loss (0.186) is on a different validation set.
For the federated-learning audience, this means you can't judge a federated foundation model by its pretraining loss. That loss looked clearly worse, but downstream prediction was equivalent and the representations were nearly the same. It is also why E09 is looking for a better checkpoint-selection metric than pretraining loss.

Optional abstract change

The current abstract says only "despite higher validation loss (0.400 vs 0.231)". To make the point explicit, change that clause in the Results to:

…despite higher pretraining loss at every seed (0.400 vs 0.231); loss did not track AUPRC (Spearman 0.08).

To make room, this version drops "Projector-plus-head fine-tuning also met the equivalence margin." The body is 2,989 characters, and 3,084 of 3,100 with the disclosure sentence. I think the loss point matters more to this audience than the projector-plus-head result, but that's your call.
