# Alyssa's five-patient synthetic handoff

The source is `examples/paulo_handoff/HANDOFF_PAULO.md`, together with its prediction JSON/CSV and pre-rendered PNG/PDF plots. The five records S01–S05 are declared synthetic by the producer. This workflow reads that bundle and creates a separate run directory; it does not rewrite the source predictions, placeholder narratives, or figures.

The updated handoff describes simulated inputs evaluated by trained XGBoost and MIL models. That model execution is producer-reported; this adapter does not rerun either predictor. Synthetic response labels remain demo scenarios, not observed clinical outcomes.

## Current packet audit

| Patient | Clinical CSV | mIF CSV | Fused CSV |
| --- | ---: | ---: | ---: |
| S01 | 0.9708 | 0.8706 | 0.9956 |
| S02 | 0.0734 | 0.1055 | 0.0093 |
| S03 | 0.1142 | 0.7966 | 0.3355 |
| S04 | 0.9643 | 0.1376 | 0.8116 |
| S05 | 0.5824 | 0.8955 | 0.9228 |

The merged handoff v3 corrects S02's mIF and fused scores, updates its mIF feature contrasts and tile features, replaces all twenty figures, and removes all alternate `prob_mif_real` fields. The CSV remains authoritative for displayed prediction scores. The producer markdown still contains old S02 scores and says tile predictions are absent; the adapter reads the actual CSV/JSON files and records their hashes.

At the demo threshold of 0.5, S03 is a fused false negative and S05 a fused false positive against the supplied synthetic labels. S04 has a positive fused display class. These are demonstration outcomes, not clinical evaluation.

All clinical JSON outputs equal the corresponding clinical CSV scores. S01/S02 SHAP reconstruction differs by 0.0001, compatible with four-decimal rounding; the importer records its tolerance and admits only numerically consistent structured SHAP as producer-declared responder-probability contributions. Partial, hash-specific visual checks of the corrected clinical PNG labels found no discrepancies. PDFs are retained without a separate visual audit. Original v2 PNG observations remain available for historical packets; corrected v3 figures no longer carry those mismatch warnings. mIF plots remain descriptive attention contrasts, without independently verified model provenance.

The two tile CSVs contain 347 tiles: `tile_features.csv` and `tile_predictions.csv`. Every supplied `tile_prob` equals the paired `attention` value. The adapter audits these files and preserves them under `ui/source_data/`; it does not expose attention weights as response probabilities in Junhao's heatmap.

For real narrative generation through the hosted NVIDIA API, see [the NIM runner](nim.md). It uses this same canonical input, interpretation skill, and report contract.

## Run the complete local plumbing

From the project root with Python 3.11+:

```bash
bash scripts/run_handoff.sh --backend mock --output-dir results/handoff-local-001
```

This imports the handoff, generates deterministic mock narratives, verifies the completed run against its canonical input, and exports a UI bundle. It needs no GPU or third-party inference packages and does not download or execute Nemotron. The exported narrative source remains visibly mock.

Each new workflow uses this layout:

```text
results/handoff-local-001/
  input/patients.jsonl       # canonical records derived from the actual source files
  experiment/               # completed narratives, manifest, review and verification artifacts
  ui/                       # copied viewer files, generated narratives, plots and warnings
```

Use a new output root for every attempt. A failed import, inference, verification or export stops subsequent stages. Earlier stage outputs remain available for diagnosis; do not reuse them as evidence that the entire workflow passed.

## Run the same cases with real Nemotron on HPC

After transferring the current project archive to approved shared HPC storage:

```bash
bash scripts/run_handoff.sh --backend vllm --output-dir results/handoff-gpu-001
```

On the current approved preparation node, this invokes the existing HPC bootstrap to create the pinned Linux Python environment and download the configured public model. It then submits one SLURM A30 job. That job imports the five handoff records, calls the existing offline GPU experiment runner, performs strict verification, and exports the UI files only when verification succeeds. The project, environment and model cache must be visible on both preparation and GPU nodes.

For an already prepared environment/cache:

```bash
bash scripts/run_handoff.sh --backend vllm --offline --output-dir results/handoff-gpu-002
```

Use `--direct` inside an existing SLURM GPU allocation. `--config config/hpc.env` selects trusted site settings, including the environment prefix, account/QOS, model identity and requested resources. `--model-path` selects a local snapshot; strict verification still requires its recorded model identity and revision to match the configuration. Full generation-setting names can follow `--`, for example `-- --batch-size 5 --max-tokens 300`; structural backend/input/output overrides are rejected.

Submission prints a job ID and the expected run root. It does not indicate completed inference. Inspect the handoff-specific tracker and logs:

```bash
COPILOT_JOB_ID=$(cat .state/last_handoff_job_id)
squeue -j "$COPILOT_JOB_ID"
tail -n 80 "logs/handoff-${COPILOT_JOB_ID}.out" "logs/handoff-${COPILOT_JOB_ID}.err"
sacct -j "$COPILOT_JOB_ID" --format=JobID,State,ExitCode,Elapsed
```

For a custom log directory, use the paths printed at submission. A successful real-model run requires all five records to be accepted native vLLM generations, the expected model ID/revision, unchanged evidence/scores and complete results. Any fallback fails strict verification and prevents UI export; completed experiment artifacts remain for inspection. Read `experiment/verification.json`, `manifest.json` and generation-review artifacts, then review every narrative. No actual A30 generation is established by local mocks or a doctor pass. See [HPC prerequisites](hpc.md).

## Preserved plots and evidence warnings

Clinical JSON is checked separately from the supplied waterfall images. Matching output and rounded additivity allow structured SHAP to enter the prompt as a source-declared attribution; this does not certify model provenance or clinical validity. Inconsistent structured SHAP is withheld. Original plots are intentionally retained for testing with visible discrepancy notes whenever a mismatch is detected, and no source score is overwritten to make a plot agree.

mIF attention contrast compares high-attention and low-attention tiles. It is not a signed effect on responder probability. The global importance JSON also remains distinct from per-patient attribution. The placeholder `narratives.json` supplied in the source is replaced only in the new UI bundle, using the generated results with source/review disclosures.

The package includes all twenty original patient PNG/PDF figures, both supplied tile tables, and the producer's documentation. Its reported real-model aggregate metrics are producer claims, separate from these five synthetic cases; this integration does not reproduce or validate those metrics. Synthetic labels are for demonstrating the viewer and must not be presented as real clinical evaluation. Genuine tile response probabilities have not been established and are not fabricated.

The original pinned UI file loader does not itself display the supplied patient plots. Use the provided local Streamlit companion for plot inspection; copying figures alone does not add a plot panel to an unchanged external viewer. Install its separate optional requirements and launch it from the project root:

```bash
python3 -m pip install -r requirements-demo.txt
streamlit run demo/handoff_app.py --server.address 127.0.0.1 \
  --browser.gatherUsageStats false -- --bundle-dir results/handoff-local-001/ui
```

Use a separate UI environment; it does not need vLLM or a GPU. Substitute the completed GPU run's `ui/` path when viewing real Nemotron output. The companion displays synthetic labels, generated narrative sources, and the retained patient plots with mismatch warnings. It does not execute inference. A completed bundle can be reviewed or copied to approved UI storage; this wrapper does not upload it or modify the external UI repository.

## Individual entry points

```bash
PYTHONPATH=src python3 -m nemotron_copilot prepare-handoff \
  --handoff-dir examples/paulo_handoff --output-dir results/handoff-input-001

PYTHONPATH=src python3 -m nemotron_copilot export-handoff-ui \
  --handoff-dir examples/paulo_handoff \
  --run-dir results/handoff-local-001/experiment --output-dir results/handoff-ui-001
```

The exporter rebuilds canonical input from the handoff and verifies the experiment's recorded input hash before attaching its plots and metadata. Changes to canonical scores, features or context require a new import and experiment. Figure bytes have separate hashes: the exporter records the figures present at export time, so a corrected plot can be re-exported alongside unchanged model input. Those hashes identify files; they do not establish that a figure explains the prediction. For future real patient inputs, define and review a separate upstream contract; keep real data within approved Moffitt storage and do not place it in this synthetic example directory or transfer archive.
