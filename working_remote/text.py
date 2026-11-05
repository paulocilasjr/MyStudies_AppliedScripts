10:59 PM
I've settled two of the three points; the TCGA count still needs one command on the HPC.

1. Dataset counts

The actual training counts are only in the HPC data manifest, not in Git, but the repo narrows them down:

GTEx (19,616): very likely correct. The 17,382 in your project plan is the GTEx V8 count (948 donors, from the V8 preprint). The builder downloads V10, whose matrix has 19,616 samples, and by default keeps all of them; only an exclude-cell-derived setting would drop any. So the reviewer saw a version change, not an error. Keep 19,616 unless the manifest shows that setting was turned on.
TCGA (10,184): probably wrong. 10,184 is the COMPASS paper's count, and the builder only enforces it if a strict-count flag is set, which is off by default. Your manifest docs say the public reconstruction gives 10,189 patients, five more than the paper. Unless your build ran in strict mode, the number you trained on is probably 10,189.
Both counts are full dataset sizes. They include the validation rows held out of training, and TCGA counts patients while GTEx counts samples. Phrasing them as dataset sizes, as the abstract does, is accurate.
Run this on the HPC and use the two numbers it prints:


python3 -c "import json,os; print(json.load(open(os.path.join(os.environ['UNIFIED_DATA_DIR'],'manifest.json')))['counts'])"
If you can't check before Nov 10, write "TCGA tumors (>10,000 patients; 33 cancer types)", which is true either way and the same length.
