# Hosted NVIDIA generation for the synthetic handoff

The `nim` backend generates the prose for the same four-part patient report through NVIDIA's hosted API. The local and HPC runners retain their existing local defaults. The hosted demo runner requires the explicitly synthetic handoff and refreshes the viewer only after every generated report passes strict verification.

The default hosted model is [`nvidia/nemotron-3-ultra-550b-a55b`](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b). This differs from the pinned `nvidia/Nemotron-Mini-4B-Instruct` used by local Transformers and vLLM runs. Hosted revisions are provider-managed, so an API model name does not identify the pinned local weight snapshot. The same prompts, report layout, and screening rules do not guarantee identical wording or model behavior. NVIDIA also provides self-hosted microservices; its [NIM offerings documentation](https://docs.nvidia.com/nim/large-language-models/latest/about-nim-llm/nim-offerings.html) describes those deployment offerings. This repository's `nim` demo uses the hosted service.

## Run the complete demonstration

From the repository root, with Python 3.11 or newer:

```bash
python3 scripts/run_nim_demo.py
```

The runner uses the Python standard library; it needs no local model download, GPU, or third-party inference package. Obtain an API key through NVIDIA's model page. If `NVIDIA_API_KEY` is absent from the process environment, the runner requests it with hidden terminal input. The key is not accepted as a command-line flag or saved in the repository, run outputs, or generated HTML. For unattended use, provide `NVIDIA_API_KEY` through the process environment or your secret manager.

The runner performs these stages:

1. Import the current handoff into a new run directory and retain its canonical input and audit.
2. Generate the three prose parts per patient through NVIDIA using the existing `build_messages` path and packaged interpretation skill.
3. Render and screen each complete report, preserving the supplied scores and evidence.
4. Verify the run with `--require-backend nim` and synthetic-input checks.
5. Export the complete handoff UI bundle and replace the saved standalone HTML only after acceptance.

A provider error, rejected report, or verification failure stops publication of the new bundle and HTML. Diagnostic experiment artifacts remain available when written. A fallback is labelled as such and fails strict hosted-generation acceptance; it is not counted as an accepted NVIDIA narrative.

Use a new output directory for each attempt. For example:

```bash
python3 scripts/run_nim_demo.py \
  --output-dir results/nim-demo-001 \
  --model-id nvidia/nemotron-3-ultra-550b-a55b \
  --json-mode json_schema
```

| Option | Purpose / default |
| --- | --- |
| `--output-dir` | New run root; the default runner selects a timestamped directory. |
| `--handoff-dir` | Synthetic source packet; default `examples/paulo_handoff`. |
| `--model-id` | Hosted model identifier; default `nvidia/nemotron-3-ultra-550b-a55b`. |
| `--json-mode` | `json_schema`, `json_object`, or `none`; default `json_schema`. |
| `--max-tokens` | Reply budget for each prose part; default `200`. |
| `--timeout` | Request timeout in seconds; default `120`. |
| `--max-retries` | Retry limit; default `2`. |
| `--html-output` | Standalone HTML destination; default `exports/ICB_Patient_Explorer.html`. |

If a selected hosted model does not support the requested structured-output mode, select a supported mode explicitly for a new run. With `none`, the prompt still asks for the same JSON reply and the application still validates its structure and content. A different mode does not bypass screening.

## What leaves this computer

Hosted inference sends the system instructions, packaged synthetic worked examples, and selected patient evidence to NVIDIA over HTTPS. The current prompt selects textual descriptions of model agreement and the computed hypothesis for the prediction summary and conclusion. Clinical interpretation receives selected feature names, source-coded values expressed as words, signed directions, and curated literature notes. These requests are external data transfers even though the supplied cases are synthetic.

Patient IDs, synthetic response labels, raw images, tile tables, full patient records, and free-form patient context are not included in the current prompts. Numeric score lines, complete feature lists, literature notes, the immune evaluation, and the final report layout are rendered by the application. The input snapshot and output reports remain local artifacts. The synthetic declaration and narrow prompt fields do not establish permission to send a different dataset; this runner is intended for the supplied synthetic demonstration.

The packaged skill and `build_messages` implementation are shared with the local backends. The application computes the classification comparison and hypothesis before generation, checks the generated prose, and preserves the same review requirement. Accepted hosted results use `narrative_source: "nim"`, with backend/model provenance, prompt identity, raw replies, and verification recorded in the experiment artifacts. The run root also saves `request_contract.json` with hashes of the exact messages for each patient/report part; a successful complete run writes `SUMMARY.md` with measured generation time and artifact paths.

## Current handoff and its remaining audit notes

The merged handoff v3 contains exactly S01–S05, with synthetic inputs and scenario labels declared by its producer. Its canonical input SHA-256 is `7e677f45d48e5a3b15c9ffdcba81706fe0e9cfd69b6218c098415260f236dbc4`. Compared with the earlier local run, the merge updates S02's mIF and fused scores, its mIF feature contrasts and tile features, replaces all twenty figures, and removes the alternate `prob_mif_real` fields. The CSV and JSON files take precedence over the producer markdown's stale S02 example.

| Patient | Clinical score | mIF score | Fused score |
| --- | ---: | ---: | ---: |
| S01 | 0.9708 | 0.8706 | 0.9956 |
| S02 | 0.0734 | 0.1055 | 0.0093 |
| S03 | 0.1142 | 0.7966 | 0.3355 |
| S04 | 0.9643 | 0.1376 | 0.8116 |
| S05 | 0.5824 | 0.8955 | 0.9228 |

All five structured clinical SHAP outputs match the clinical CSV scores and pass the declared rounding checks. Partial, hash-specific visual checks of the corrected clinical PNG labels found no discrepancies against those records. This is not complete image validation; PDFs have not been individually visually audited. The old clinical-image and alternate-score mismatch warnings no longer apply to this packet; tests retain coverage for such inconsistencies.

All 347 supplied `tile_prob` values still duplicate attention weights. The exporter preserves these tables under `ui/source_data/` without presenting them as tile response probabilities. mIF attention contrasts remain descriptive, not signed responder attributions. The response endpoint is still unspecified and calibration unknown; synthetic labels do not establish clinical performance. See the [handoff audit guide](handoff.md) for the checks and source semantics.

## Completed hosted test

The accepted v3 run is `results/nim-demo-20261014T152515Z/`. It generated all five reports in 55.629 seconds: 15 accepted replies across 17 API attempts, with two retries. All reports passed the existing heuristic screen and strict hosted verification. Reported usage was 18,353 prompt tokens and 1,125 completion tokens. These are measured results from this run, not latency or token-cost guarantees.

All 15 recorded message hashes match the shared local prompt builder and interpretation skill. The exact input snapshot changed with v3, but the selected prompts match the previous local input: S02 stayed in the same score-threshold bands, and the selected clinical attributions did not change. The renderer uses the corrected exact scores and full mIF evidence. `input_parity.json` records this distinction. The generated clinical prose still needs independent review; passing the application checks does not establish clinical correctness.

The UI bundle is `results/nim-demo-20261014T152515Z/ui/`, and `exports/ICB_Patient_Explorer.html` embeds that completed run. Run artifacts are local and ignored by Git; the shareable HTML contains the saved snapshot.

## Individual CLI steps and viewer refresh

The lower-level CLI reads `NVIDIA_API_KEY` from the environment only. It does not prompt for a key. To run the stages separately, with the key already supplied to the process:

```bash
PYTHONPATH=src python3 -m nemotron_copilot prepare-handoff \
  --handoff-dir examples/paulo_handoff \
  --output-dir results/nim-manual-001/input

PYTHONPATH=src python3 -m nemotron_copilot experiment \
  --backend nim --nim-model nvidia/nemotron-3-ultra-550b-a55b \
  --nim-json-mode json_schema \
  --input results/nim-manual-001/input/patients.jsonl \
  --output-dir results/nim-manual-001/experiment

PYTHONPATH=src python3 -m nemotron_copilot verify-run \
  --input results/nim-manual-001/input/patients.jsonl \
  --output-dir results/nim-manual-001/experiment \
  --require-backend nim --require-synthetic
```

Continue only after verification passes. Export the whole bundle to keep the prediction CSV, narrative strings, structured reports, audit, and provenance consistent:

```bash
PYTHONPATH=src python3 -m nemotron_copilot export-handoff-ui \
  --handoff-dir examples/paulo_handoff \
  --run-dir results/nim-manual-001/experiment \
  --output-dir results/nim-manual-001/ui

PYTHONPATH=src python3 scripts/export_standalone_demo.py \
  --bundle-dir results/nim-manual-001/ui \
  --output exports/ICB_Patient_Explorer.html
```

Open `exports/ICB_Patient_Explorer.html` to inspect the five saved reports. It embeds the complete exported snapshot, works offline, and does not regenerate text when switching patients. Refresh or reopen an already open HTML page after replacing its file.

For the optional Streamlit companion, use an environment with `requirements-demo.txt` installed:

```bash
streamlit run demo/handoff_app.py \
  --server.address 127.0.0.1 --browser.gatherUsageStats false \
  -- --bundle-dir results/nim-manual-001/ui
```

Point a fresh viewer process at the new bundle directory. The companion reads the structured report from `copilot_results.jsonl` and checks it against `narratives.json`; editing only the latter does not update the main displayed report. An older viewer process or copied bundle continues to show its saved reports. This launch displays the completed hosted run; live regeneration is a separate optional API connection.
