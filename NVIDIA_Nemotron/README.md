# ICB Response Prediction — Nemotron Copilot

This is Paulo's interpretive layer for the hackathon. It accepts clinical, multiplex immunofluorescence (mIF), and late-fusion prediction scores, then produces reviewable research summaries for Junhao's demo. It runs independently of the prediction models, so integration can start with the included synthetic cases.

The default inference paths use NVIDIA's `Nemotron-Mini-4B-Instruct` weights locally through vLLM or Hugging Face Transformers. NVIDIA describes this general-purpose model for roleplaying, retrieval-augmented generation, and function calling; this repository does not establish clinical validity. See the [NVIDIA model card](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct). An explicit `nim` backend also supports NVIDIA's hosted API for the synthetic demonstration, using `nvidia/nemotron-3-ultra-550b-a55b` by default. It sends the selected prompt evidence to NVIDIA and records its hosted provenance separately; see the [hosted NVIDIA guide](docs/nim.md).

The input is **predictions already produced by the clinical/mIF/fusion models**, plus patient evidence and context. This component does not train those predictors or calculate predictions directly from raw clinical tables, slides, or images. The response endpoint remains undecided.

## Run the complete MVP locally with the real model

On an Apple Silicon Mac (or another computer with Python 3.11–3.13), one command runs the whole demonstration with real Nemotron inference and opens the connected viewer:

```bash
bash run_local_mvp.sh
```

The first run creates `.envs/local-mvp` from `requirements-local.txt` and downloads the pinned public `Nemotron-Mini-4B-Instruct` snapshot (about 8.4 GB) into `.cache/huggingface/hub`. Later runs reuse both and stay offline. The script then:

1. imports Alyssa's five synthetic patients;
2. generates their narratives on this computer (Apple MPS through Hugging Face Transformers);
3. verifies the run and exports the viewer bundle;
4. starts the loopback copilot API and opens the Streamlit viewer connected to it.

Each patient gets a structured report with four parts:
1. **Model evaluation predictions:** the three scores and what they imply, including the strongest hypothesis or the conflict and tendency.
2. **Clinical evaluation:** features towards responder and towards non-responder, by SHAP sign, with literature notes.
3. **Immune evaluation:** each mIF feature with its literature note and classification direction.
4. **Conclusions.**

The application prints the scores, feature lists, cited literature notes, and the hypothesis it computes. Nemotron writes the short prose of parts 1, 2 and 4, one focused prompt per part. On an M3 Pro, generation takes about two minutes for five patients.

Each patient page in the viewer can regenerate its report live through the local API. Only the patient's supplied evidence is sent, never its label. Press Ctrl+C to stop the API and viewer.

Each run writes a new `results/local-mvp-<timestamp>/` root containing `SUMMARY.md` (every patient's report and the output files), `input/`, `experiment/`, `ui/`, `live_api_check.json` and `logs/`. To reopen a completed run without regenerating, use `bash run_local_mvp.sh --reuse-run results/local-mvp-<timestamp>`. `--no-ui` stops after the outputs, and `--help` lists the device and port options.

Local results record `narrative_source: "transformers"`, distinct from HPC `vllm` output. The weights, revision, prompt and greedy settings are the same. vLLM's JSON-schema guided decoding is replaced by a forced `{"text": "` reply prefix, so wording can differ from an A30 run. On MPS the backend uses eager attention, because PyTorch 2.8's half-precision scaled-dot-product attention produces only padding tokens at this prompt length. The automated screen applies unchanged: if any generated part is rejected, the report uses labelled deterministic prose for all three parts, and the run summary reports it. Behind an institutional TLS-inspection proxy, `prepare-model` uses the operating system's certificate store via `truststore`.

## Generate the five synthetic reports through NVIDIA's hosted API

With Python 3.11 or newer, run:

```bash
python3 scripts/run_nim_demo.py
```

The runner uses the Python standard library and prompts for `NVIDIA_API_KEY` with hidden input if it is absent from the environment. The key is kept out of command arguments and saved artifacts. It imports the current S01–S05 handoff, sends the same focused report prompts and interpretation skill to NVIDIA, verifies that every report contains accepted `nim` generation, then exports a new UI bundle and refreshes `exports/ICB_Patient_Explorer.html`. Open that HTML file to view the saved patient reports without running a server. A failed generation or strict verification leaves diagnostic results and stops the export.

This is an external inference request using a different model from the local Mini 4B. The current prompts send selected textual evidence about score agreement, the computed hypothesis, and clinical feature names, values, directions, and curated literature notes, plus the packaged instructions and synthetic examples. Patient IDs, response labels, raw images, and free-form patient context are excluded. The same report rendering and screening pipeline applies, while wording and model behavior can differ. Hosted model revisions are provider-managed. See [NVIDIA's model page](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b) and the [hosted guide](docs/nim.md) for model selection, options, data flow, and viewer refresh commands. Local inference remains the default for the existing local and HPC runners.

## Run the local demonstration

From this folder, with Python 3.11 or newer:

```bash
bash scripts/run_local.sh
```

The runner uses your existing Python and executes a deterministic `mock` experiment using `examples/mock_predictions.jsonl`. It needs no third-party packages, GPU, model download, or real patient data. The four synthetic cases cover concordant predictions, disagreement between modalities, clinical data alone, and scores near a supplied threshold. A successful mock run verifies the interfaces and output plumbing; it does not verify Nemotron inference or prediction quality.

## Test Alyssa's five-patient handoff

The supplied `examples/paulo_handoff/` packet includes synthetic patients S01–S05, three prediction scores per patient, and clinical SHAP/mIF plots. Run its complete import, narrative generation, verification, and UI export locally:

```bash
bash scripts/run_handoff.sh --backend mock --output-dir results/handoff-local-001
```

Use a new output directory for each run. The `input/` folder contains canonical patient JSONL and an audit; `experiment/` contains structured narratives and verification; `ui/` contains scores, generated narrative JSON, and all twenty original PNG/PDF figures. The supplied placeholder narratives are excluded. In the merged v3 packet, clinical SHAP JSON agrees with clinical scores within the declared rounding checks; corrected clinical PNG labels pass the recorded partial visual checks. The merge updates S02’s mIF and fused scores and removes the conflicting `prob_mif_real` fields. The `tile_prob` column still duplicates tile attention weights; the audit keeps tile tables under `ui/source_data/`, outside the response-probability heatmap contract.

The local companion adds a patient dropdown and both figure panels to the compatible UI bundle. In a separate Python environment:

```bash
python3 -m venv .envs/handoff-demo
.envs/handoff-demo/bin/python -m pip install -r requirements-demo.txt
.envs/handoff-demo/bin/streamlit run demo/handoff_app.py \
  --server.address 127.0.0.1 --browser.gatherUsageStats false \
  -- --bundle-dir results/handoff-local-001/ui
```

For real Nemotron generation on HPC, use `bash scripts/run_handoff.sh --backend vllm --output-dir results/handoff-gpu-001`. It prepares the pinned environment/model, submits an A30 job, and exports UI files only after strict real-generation verification passes. See the [handoff guide](docs/handoff.md) for monitoring, offline runs, individual entry points, and plot limitations. The unchanged external UI can load the basic scores/narratives; patient-specific plots require this companion or a corresponding UI extension.

## Run on Moffitt's HPC

Copy this folder to an approved shared HPC project location, then run from the copied folder:

```bash
bash run_hpc.sh --smoke
```

The runner submits a SLURM job on the `red` partition with one A30 GPU, creates an isolated Python environment, prepares the pinned public model snapshot, and executes the synthetic experiment. First-time setup needs access to package and model repositories. Later inference uses the local model files with offline settings. This HPC runner does not send patient inputs to a hosted inference API; the separate, explicitly selected `nim` backend does send its prompts to NVIDIA.

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

## Prepare patient inputs and review the prompt

Start with [patient input guidance](docs/patient_inputs.md) and the fully synthetic `examples/patient_template.json`. The six-case `examples/prompt_quality_cases.jsonl` additionally exercises absent thresholds and instruction-like context. Do not copy its synthetic scores into study records.

The packaged [interpretation skill](src/icb_copilot/skills/icb-interpretation/SKILL.md) and its worked examples build one focused system prompt per report part, including after wheel installation. The skill gives the model a compact summary of the project and its foundation study. Two references stay out of the 4,096-token prompt:
- the full background, in the [project context reference](src/icb_copilot/skills/icb-interpretation/references/project-context.md);
- the cited per-feature literature, in [feature-literature.json](src/icb_copilot/skills/icb-interpretation/references/feature-literature.json).

The application computes the comparison, the plain-word `situation` and the strongest hypothesis, and keeps labels out of the prompt. The screen rejects generated statements that contradict those facts or the SHAP directions. Prompt version and SHA-256 are recorded per result. [Prompt review and HPC commands](docs/prompt_review.md) explain raw reply inspection, strict real-model acceptance, and the remaining GPU verification step.

## Read an experiment's outputs

| Artifact | Purpose |
| --- | --- |
| `narratives.jsonl` | One structured result per patient, including the four-part report (`narrative`), unchanged input predictions, limitations, quality status, and provenance. Recommended UI input. |
| `generation_review.jsonl` | Raw model replies, screen issues, and prompt version/hash for prompt review. Mock runs contain null replies; this file is not UI narrative input. |
| `narratives.csv` | Compact patient summaries for tabular inspection. |
| `report.md` | Human-readable experiment report. |
| `manifest.json` | Run configuration, input identity, backend, and runtime provenance. |
| `metrics.json` | Available prediction evaluation; unlabeled synthetic cases cannot establish predictive performance. |

Every result requires human review. `narrative_source` distinguishes deterministic `mock` text, local `vllm` or `transformers` output, hosted NVIDIA `nim` output, and a deterministic `fallback`. A quality check can reject generated text and replace it with a grounded fallback; passing that check only means the implemented checks passed. It does not establish medical correctness. The UI should display the source, limitations, and review flag alongside the narrative.

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
