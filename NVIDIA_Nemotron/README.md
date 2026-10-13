# ICB Response Prediction — Nemotron Copilot

This is Paulo's interpretive layer for the hackathon. It accepts clinical, multiplex immunofluorescence (mIF), and late-fusion prediction scores, then produces reviewable research summaries for Junhao's demo. It runs independently of the prediction models, so integration can start with the included synthetic cases.

The local GPU backend uses NVIDIA's `Nemotron-Mini-4B-Instruct` weights through vLLM. NVIDIA describes this general-purpose model for roleplaying, retrieval-augmented generation, and function calling; this repository does not establish clinical validity. See the [NVIDIA model card](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct). The implementation is a local vLLM deployment; NVIDIA NIM is a separate serving product.

The input is **predictions already produced by the clinical/mIF/fusion models**, plus patient evidence and context. This component does not train those predictors or calculate predictions directly from raw clinical tables, slides, or images. The response endpoint remains undecided.

## Run the local demonstration

From this folder, with Python 3.11 or newer:

```bash
bash scripts/run_local.sh
```

The runner uses your existing Python and executes a deterministic `mock` experiment using `examples/mock_predictions.jsonl`. It needs no third-party packages, GPU, model download, or real patient data. The four synthetic cases cover concordant predictions, disagreement between modalities, clinical data alone, and scores near a supplied threshold. A successful mock run verifies the interfaces and output plumbing; it does not verify Nemotron inference or prediction quality.

## Run on Moffitt's HPC

Copy this folder to the approved HPC project location, for example under `/share/lab_goecks/Alyssa/Markowitz/feb2026/`, then run from the copied folder:

```bash
bash run_hpc.sh --smoke
```

The runner submits a SLURM job on the `red` partition with one A30 GPU, creates an isolated Python environment, prepares the pinned public model snapshot, and executes the synthetic experiment. First-time setup needs access to package and model repositories. Later inference uses the local model files with offline settings. Patient inputs are not sent to a hosted inference API.

`--smoke` then writes `verification.json` and requires every synthetic narrative to come from real vLLM generation and pass the implemented screen. A mock backend, injected test generator, changed scores, or any fallback narrative fails this acceptance check. Results remain available for diagnosis. Passing the check verifies execution and interfaces; it does not certify clinical correctness. Submission prints a job ID and returns before the GPU job finishes.

If compute nodes cannot download packages or weights, prepare on an approved internet-connected login node first:

```bash
bash run_hpc.sh --prepare-only
bash run_hpc.sh --smoke --offline
```

See [HPC setup and operation](docs/hpc.md) for site configuration, offline staging, driver compatibility, and diagnosing failures. The local computer cannot verify SLURM submission, the site's installed GPU driver, or a real A30 model load; the first HPC run completes that verification.

For a clean transfer, `python3 scripts/package_hpc.py` produces a code-and-synthetic-fixture archive under `dist/`, excluding local inputs, runs, caches and environments. The [first-run terminal guide](docs/first_hpc_smoke.md) includes transfer, extraction, setup/submission, job monitoring, acceptance, and UI export commands.

## Feed the existing melanoma demo UI

[Junhao's Streamlit UI](https://github.com/qchiujunhao/melanoma-demo-ui) reads a prediction CSV and a JSON dictionary of narrative strings. It does not directly load the copilot JSONL or call the copilot API. After a completed run, export its files:

```bash
PYTHONPATH=src python -m nemotron_copilot export-ui \
  --run-dir results/gpu-smoke-JOBID \
  --output-dir results/ui-smoke-JOBID
```

Replace `JOBID` with the submitted job number. The exporter preserves structured results alongside the UI files, carries review/source/quality/limitations into the displayed narrative, and records exclusions. The current UI requires all three scores and fixes its display threshold at 0.5: clinical-only patients are excluded from its prediction CSV, and incompatible or missing supplied thresholds cause export to fail. No missing score, label, global importance, or image is invented. See the [UI compatibility guide](docs/demo_ui.md) for the exact file layout, optional label export, launch command, and UI changes still needed for the full cohort.

## Connect the prediction models

Isis, Alyssa, and the fusion owner export one prediction CSV each. The join key is the study's canonical pseudonymous `patient_id`; slide identifiers must be mapped upstream. The copilot assembles records by ID, preserves missing modalities, and never invents a fused score.

```bash
PYTHONPATH=src python -m nemotron_copilot assemble \
  --clinical-csv examples/upstream/clinical_predictions.csv \
  --mif-csv examples/upstream/mif_predictions.csv \
  --fused-csv examples/upstream/fused_predictions.csv \
  --context-jsonl examples/upstream/clinical_context.jsonl \
  --output results/assembled.jsonl

PYTHONPATH=src python -m nemotron_copilot validate --input results/assembled.jsonl

bash run_hpc.sh --offline \
  --input results/assembled.jsonl \
  --output-dir results/copilot-real
```

Use the same CSV headers with real upstream files once those models are ready. The [team integration contract](docs/integration.md) specifies fields, attribution semantics, and the local HTTP endpoints for Junhao's UI. `src/nemotron_copilot.py` is the public integration facade; the implementation lives in `src/icb_copilot/`.

## Read an experiment's outputs

| Artifact | Purpose |
| --- | --- |
| `narratives.jsonl` | One structured result per patient, including the narrative, unchanged input predictions, limitations, quality status, and provenance. Recommended UI input. |
| `narratives.csv` | Compact patient summaries for tabular inspection. |
| `report.md` | Human-readable experiment report. |
| `manifest.json` | Run configuration, input identity, backend, and runtime provenance. |
| `metrics.json` | Available prediction evaluation; unlabeled synthetic cases cannot establish predictive performance. |

Every result requires human review. `narrative_source` distinguishes deterministic mock text, Nemotron output, and a deterministic fallback. A quality check can reject generated text and replace it with a grounded fallback; passing that check only means the implemented checks passed. It does not establish medical correctness. The UI should display the source, limitations, and review flag alongside the narrative.

## Interpret the demonstration accurately

`probability` always refers to the supplied model's positive label, **ICB responder**. Unknown calibration means scores should not be presented as validated individual outcome probabilities. Feature `direction` describes the measurement, such as “high” or “elevated”; it does not establish that the feature supports response. Signed model attributions are a separate optional field.

The team has not yet decided the responder endpoint. Real exports should retain `response_definition: "Not specified"` until it is agreed; the experiment then flags the missing definition and excludes those records from performance evaluation. The first narrative sentence reports supplied scores and up to two features per modality; full features and context remain in the structured output. Numeric scores in the prose are rounded to three decimal places, while the structured predictions retain their supplied values.

The copilot can explain concordance, disagreement, and missing modalities. A change from a single-modality score to a fused score does not prove better prediction or improved patient outcomes. Compare the models on the same held-out patients, with the same response endpoint, before making a performance claim. See [research evaluation and narrative review](docs/research_review.md).

Treatment selection, medication changes, clinical-trial eligibility, cancer screening, and care decisions are outside this hackathon component's implemented scope. The current deliverable is research interpretation of ICB response scores.

## Development checks

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The test suite checks contracts, integration, and narrative behavior with lightweight backends. GPU inference remains an HPC verification step.
