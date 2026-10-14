# Connecting the actual melanoma demo UI

The copilot accepts precomputed clinical, mIF, and fused ML scores together with patient-level features and supplied clinical context. It returns a structured JSON result and produces batch artifacts. It does not load or train those prediction models, infer a missing fused score, or read raw clinical/mIF datasets automatically. Upstream producers supply canonical records or the documented prediction CSVs plus a context/features sidecar.

The inspected UI is [qchiujunhao/melanoma-demo-ui](https://github.com/qchiujunhao/melanoma-demo-ui), pinned for this audit to commit [`59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f`](https://github.com/qchiujunhao/melanoma-demo-ui/commit/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f). It is a Streamlit viewer for local files. It does not currently call the copilot HTTP API, run Nemotron, or read `narratives.jsonl` directly.

## Actual viewer contract

For Alyssa's five synthetic S01–S05 cases, use the [dedicated handoff workflow](handoff.md). It preserves the supplied labels explicitly as synthetic demonstration data and bundles original clinical SHAP/mIF figures with mismatch notes. A follow-up inspection of UI commit [`4306ad74eb3bfa6ed0bb330a397dd6b5cd40fbed`](https://github.com/qchiujunhao/melanoma-demo-ui/commit/4306ad74eb3bfa6ed0bb330a397dd6b5cd40fbed) confirmed that patient-specific feature-analysis/figure rendering still needs a UI extension. This repository's `demo/handoff_app.py` provides that local viewer. Use it for the five-patient test; any ROC displayed by the external UI using these fabricated labels is illustrative only.

| File under the UI's `results/predictions/` | Actual parser requirement |
| --- | --- |
| `patient_predictions.csv` | Required columns exactly named `Patient_id`, `prob_mif`, `prob_clinical`, `prob_fused`, `actual_response`. Extra columns are accepted but not automatically displayed. |
| Patient scores | All three are required and must be finite numbers in `[0,1]` for every patient; blank/NaN scores fail the required file. |
| Patient ID | Nonempty unique string; outer CSV whitespace is stripped and leading zeros are preserved. |
| `actual_response` | Required column; `0`, `1`, or blank. Unknown labels are accepted and excluded from ROC analysis. |
| `narratives.json` | Optional object mapping IDs to nonempty strings, for example `{"P48":"Research narrative..."}`. Narrative IDs must be a subset of the prediction CSV IDs. |
| `feature_importances.json` | Optional **global** `clinical`/`mif` lists with `feature` and finite `importance`; signed values are permitted. Patient-level SHAP values must not be relabeled as global importance. |
| `tile_predictions.csv` | Optional genuine tile scores and coordinates, with patient IDs matching the required CSV. Do not create tiles by copying patient scores. |

The loader blocks an invalid/missing required prediction file. Invalid/missing optional files leave their panels empty with readiness information; it does not silently substitute synthetic files. The bundled UI synthetic data contains 19 invented cases and differs from this repository's four fixtures, even where patient IDs overlap. Do not join the two fixture datasets simply because an ID matches.

Exact sources: [UI data contract](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/docs/DATA_CONTRACT.md), [prediction/narrative parsers](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/data_loader.py#L39), [bundle loading](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/data_loader.py#L103), and [ROC calculation](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/data_loader.py#L137).

## Local adapter

Export a **completed** copilot experiment to a new local bundle directory:

```bash
PYTHONPATH=src python -m nemotron_copilot export-ui \
  --run-dir results/copilot-run-001 \
  --output-dir results/ui-bundle-001
```

This writes the required prediction CSV and narrative JSON with the viewer's exact field names. It also writes `copilot_results.jsonl`, `copilot_manifest.json`, and `ui_export_manifest.json` to preserve the complete results/provenance and disclose patient exclusions. The pinned viewer ignores these extra sidecars; they remain available for review and future UI integration.

The adapter includes only patients with **all three scores**. Clinical-only or other incomplete cases are explicitly listed in the export manifest rather than filled with zero or fabricated fusion. The original full result JSONL still contains excluded cases. If all patients are incomplete, export fails. For the included patients, every supplied decision threshold must be exactly `0.5`; absent or different thresholds fail export because the current UI imposes its own fixed 0.50 classification. Do not alter upstream thresholds merely to satisfy the viewer. A UI change is needed to display arbitrary thresholds or missing classifications honestly.

The text mapping includes the declared narrative source (`mock`, `vllm`, or `fallback`), automated quality state, review requirement, full-precision scores, producer-declared calibration, and all limitations. An injected test generator is explicitly identified. These details are placed inside plain displayed narrative text because the current viewer does not render the structured metadata separately. In particular, a mock/fallback result is not presented as proof of real Nemotron inference.

Only critical structural/provenance consistency is checked: canonical evidence, unique IDs, review/source/quality fields, comparison/classification logic, deterministic numeric prefix/review suffix, and manifest counts. These checks are not an independent medical-quality validator. Schema revisions or changes in the remote viewer contract require reviewing/updating this adapter.

## Optional observed labels

Interpretation results intentionally omit `ground_truth` and `evaluation_partition`, so export writes blank `actual_response` values by default. The viewer can still display scores/narratives; ROC is unavailable when no valid labels are supplied.

To export eligible existing labels, explicitly supply the exact canonical input snapshot used by the run:

```bash
PYTHONPATH=src python -m nemotron_copilot export-ui \
  --run-dir results/copilot-run-001 \
  --output-dir results/ui-bundle-001 \
  --input results/predictions/copilot_input.jsonl
```

The input bytes must match the experiment's SHA-256, patient IDs, and normalized prediction/features/context evidence. Labels are included only when known, declared `test` or `out_of_fold`, and associated with a specified response endpoint; other labels remain blank with recorded reasons. The current viewer pools labeled patients for ROC, so export rejects more than one eligible endpoint/partition group. Build a coherent evaluation bundle upstream rather than pooling incompatible groups.

Held-out status, endpoint validity, calibration, and labels remain producer declarations requiring study review. The responder definition is still an open team decision. A nonempty arbitrary definition does not validate an endpoint. No label is inferred from a score, invented for the demonstration, or restored merely by finding a patient ID.

## Demonstrate with this repository's synthetic cases

```bash
bash scripts/run_local.sh --output-dir results/ui-smoke-run

PYTHONPATH=src python -m nemotron_copilot export-ui \
  --run-dir results/ui-smoke-run \
  --output-dir results/ui-smoke-bundle \
  --input examples/mock_predictions.jsonl
```

The expected viewer subset is P48, P12, and P29. P07 is clinical-only and is recorded as excluded. Labels remain blank because the synthetic inputs have unknown labels and are not eligible research evaluation records. All displayed text identifies mock generation. This verifies file mapping and synthetic workflow behavior; it does not execute the GPU model.

After a real synthetic-input HPC experiment, run the same export command on its completed output folder. Inspect `source_counts`, `quality_counts`, results, and logs before claiming real accepted LLM generation. A vLLM run using an injected test generator or only deterministic fallbacks does not establish usable actual Nemotron output.

## Launch the viewer with a fresh bundle

The original contract was audited against the [UI README](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/README.md) launches the app from its repository root with `streamlit run src/app.py --server.port 8501`, after creating a Python 3.11+ environment and installing `requirements.txt`. Its tracked [Streamlit configuration](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/.streamlit/config.toml) binds loopback and disables browser usage statistics. The example below makes the loopback address explicit.

Use a **fresh local checkout** on approved storage and a separate UI environment. Place the completed bundle next to the checkout as `copilot-ui-bundle`, or adjust the relative source path below:

```bash
umask 077
git clone https://github.com/qchiujunhao/melanoma-demo-ui.git melanoma-demo-ui-fresh
cd melanoma-demo-ui-fresh
git checkout --detach 4306ad74eb3bfa6ed0bb330a397dd6b5cd40fbed
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import shutil; shutil.copytree('../copilot-ui-bundle', 'results/predictions')"
streamlit run src/app.py --server.port 8501 --server.address 127.0.0.1
```

`copytree` deliberately fails if `results/predictions/` already exists. Use a fresh checkout or deliberately review/archive the prior local bundle before another copy; do not merge new files into an old predictions directory. This prevents stale optional `feature_importances.json` or `tile_predictions.csv` from remaining visible when the new copilot bundle does not supply them. In particular, do not copy the UI's unrelated `demo_data/` fixtures into the copilot bundle or the output directory.

Open the local address printed by Streamlit, select **Local output files**, and click **Reload files**. The app initially selects **Synthetic demo**, so it will otherwise continue showing its own 19 fixtures. The file source toggle only selects the local directory; the narrative text still identifies the scores/summary as a mock demonstration. Missing global importance and tile panels should remain empty.

On the HPC, run the UI in the approved compute environment and use the site's approved tunnel/access arrangement. A loopback binding does not make a remote compute-node port directly reachable from the presentation computer. Public source/package preparation and local file copying do not upload the bundle to GitHub; this workflow leaves the external repository unchanged.

## Remaining UI gaps

The current app reads only its local `demo_data/` or `results/predictions/` directories. The adapter does not clone, change, publish, or upload anything to the external repository.

- **Missing modalities:** the viewer rejects incomplete score rows. It needs a schema/layout change to display the clinical-only cohort.
- **Thresholds:** it always classifies at 0.50, independently of upstream model metadata. Strict export rejects incompatible thresholds instead of silently redefining classifications.
- **Calibration:** cards are labeled `P(response)` even for uncalibrated scores. Narrative disclosure is useful, but the UI should ultimately display calibration status and use appropriate score language.
- **Source and review:** the viewer displays a generic pre-generated narrative caption. Exported text distinguishes mock, fallback, and screened model outputs; the viewer does not yet expose structured quality metadata.
- **Patient evidence:** existing importance panels are global. They do not display the patient's full clinical context, measured values, signed attributions, or model/feature provenance from the structured sidecar.
- **ROC grouping/provenance:** the viewer uses every row with a known label, without checking endpoint/partition metadata. The adapter restricts exported labels, but producers still need to verify split independence.
- **Display precision:** percentage cards round to one decimal percent. Classification uses the unrounded CSV score, so near-threshold values can look tied; the narrative retains full precision for review.
- **API integration:** there is no live copilot request path. Any future Streamlit server-side API integration should preserve the result metadata rather than reducing it to text.

These behaviors are visible in [app.py](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/app.py#L53), including the [fixed threshold and score formatting](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/app.py#L85) and [plain narrative display](https://github.com/qchiujunhao/melanoma-demo-ui/blob/59b7f0f3f864aef3a5d95ca9af4c2acfdb928a7f/src/app.py#L127). No global importance or tile file is synthesized by this adapter.
