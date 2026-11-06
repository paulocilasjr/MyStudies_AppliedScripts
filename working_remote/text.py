Check these before pasting:

Placeholders. Replace [R] and [E] with your FedAvg settings.
Site partition. I assumed the sites were split by data source (all TCGA at one site, all GTEx at the other). You didn’t confirm this. If the split was random, change “partitioned by source” to “with a random split.”
CKA and Spearman wording. I read your original as comparing federated–pooled similarity against pooled–pooled similarity. Correct it if that’s wrong.
“Prespecified.” If the ±0.078 margin was fixed before you looked at model scores, add that word. Leave it out if it wasn’t.
