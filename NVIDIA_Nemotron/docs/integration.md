# Team integration contract

The public entry points are the `nemotron_copilot` Python module, its CLI, and a local HTTP service. They use one versioned patient-record contract. Python imports do not load weights; create and reuse one `Copilot` instance when an application starts.

## Responsibilities and join key

| Owner | Export or consume |
| --- | --- |
| Isis | Clinical prediction CSV and clinical feature/context metadata. |
| Alyssa | mIF prediction CSV and mIF feature/attribution metadata. Map slide IDs to canonical patient IDs upstream. |
| Fusion owner | Fused prediction CSV from the late-fusion model, with its own model ID, threshold, and calibration metadata. |
| Paulo | Validate/assemble records; generate grounded research narratives and provenance using the local backend. |
| Junhao | Load `narratives.jsonl` or call the local API; show the patient selector, modality scores, evidence, limitations, source, and review status. |

Use the same pseudonymous `patient_id` across all modalities. Each patient appears once per modality CSV. Missing mIF is expected for clinical-only patients; omit that prediction rather than substitute zero. Fusion is supplied by the modeling pipeline, not computed by this copilot.

## Canonical patient input

JSONL means one JSON object per nonempty line, with UTF-8 encoding. The complete synthetic dataset is `examples/mock_predictions.jsonl`.

```json
{
  "schema_version": "1.0",
  "patient_id": "P48",
  "predictions": {
    "clinical": {
      "probability": 0.85,
      "model_id": "clinical-synthetic-v1",
      "calibration": "unknown",
      "decision_threshold": 0.5
    },
    "mif": {
      "probability": 0.79,
      "model_id": "mif-synthetic-v1",
      "calibration": "unknown",
      "decision_threshold": 0.5
    },
    "fused": {
      "probability": 0.82,
      "model_id": "fusion-synthetic-v1",
      "calibration": "unknown",
      "decision_threshold": 0.5
    }
  },
  "top_features": {
    "clinical": [
      {
        "feature": "LDH level",
        "value": 389,
        "unit": "U/L",
        "direction": "elevated",
        "attribution": null
      }
    ],
    "mif": [
      {
        "feature": "CD3+ CD8+ Ripley's L (20um)",
        "value": 45.2,
        "unit": "um",
        "direction": "high",
        "attribution": {
          "method": "shap",
          "value": 0.2,
          "scale": "log_odds"
        }
      }
    ]
  },
  "clinical_context": "Synthetic example only; supplied study context.",
  "response_definition": "Synthetic ICB responder label; no clinical endpoint specified.",
  "ground_truth": null,
  "evaluation_partition": "synthetic"
}
```

| Field | Rules |
| --- | --- |
| `schema_version` | `"1.0"`; omitted values default to the supported version. |
| `patient_id` | Required pseudonymous ID, at most 100 characters, using letters, numbers, `_ . : -`; must start with a letter or number. |
| `predictions` | Required nonempty object; any subset of `clinical`, `mif`, `fused`. |
| `probability` | Required finite number in `[0,1]`; the positive class is always **ICB responder**. |
| `model_id` | Upstream model identifier; defaults to `"unspecified"`. Include a version or experiment identifier. |
| `calibration` | `"unknown"`, `"uncalibrated"`, or `"calibrated"`; defaults to `"unknown"`. This metadata is supplied by the modeling team, not assessed by the LLM. |
| `decision_threshold` | Finite number in `[0,1]`, or `null`/omitted. A score at or above the supplied threshold maps to responder. No threshold is inferred. |
| `top_features` | Optional modality objects containing at most 10 unique feature names each. Features require a corresponding prediction. |
| `clinical_context` | Optional supplied context, at most 2,000 characters; defaults to an empty string. Use approved, minimal study context. |
| `response_definition` | Optional endpoint description, at most 500 characters; defaults to `"Not specified"`. Include the actual endpoint and assessment window when known. |
| `ground_truth` | Integer `1` for responder, `0` for non-responder, or `null`/omitted. Used for experiment evaluation, not provided to narrative generation. |
| `evaluation_partition` | `"unspecified"`, `"train"`, `"validation"`, `"test"`, `"out_of_fold"`, or `"synthetic"`; defaults to `"unspecified"`. |

Unsupported fields are rejected to expose integration mistakes early. JSON numbers must be finite; string probabilities and booleans are not probability values. Duplicate patient IDs in an input batch are rejected.

A feature requires its `feature` name and may supply `value` as a finite number, string, boolean, or `null`. `unit` is optional. `direction` defaults to `"not supplied"` and describes a measurement relative to a supplied reference. Do not use it as an attribution sign. `attribution` is optional or `null`; when present it requires a method, signed finite value, and scale. Examples of scales are `log_odds` and `probability`, but their meaning must match the upstream explainer. The attribution sign must refer to the responder class. Do not compare attribution magnitudes across different models or scales as if they shared one baseline.

## CSV exports and context sidecar

Each modality CSV uses this header:

```csv
patient_id,probability,model_id,calibration,decision_threshold
P48,0.85,clinical-synthetic-v1,unknown,0.5
```

`patient_id` and `probability` are required columns. Optional metadata columns can be omitted. If a threshold is unavailable, leave it blank; never fill it with a default solely for display. Use a header-only file or omit the modality file when no predictions exist for that modality.

The optional context JSONL sidecar has one record per `patient_id` with any of `top_features`, `clinical_context`, `response_definition`, `ground_truth`, and `evaluation_partition`. It supplies evidence/context separately from model probabilities. See `examples/upstream/clinical_context.jsonl`. Sidecar IDs must refer to patients exported by at least one model.

```bash
PYTHONPATH=src python -m nemotron_copilot assemble \
  --clinical-csv examples/upstream/clinical_predictions.csv \
  --mif-csv examples/upstream/mif_predictions.csv \
  --fused-csv examples/upstream/fused_predictions.csv \
  --context-jsonl examples/upstream/clinical_context.jsonl \
  --output results/assembled.jsonl
```

Assembly joins by patient ID and validates the resulting contract. The copilot expects one resolved slide-to-patient mapping and one prediction per patient; it does not average repeated rows or decide which duplicate to trust.

## Python entry point

Make `src/` importable (`PYTHONPATH=src` from this folder, or install the project), then use:

```python
import json
from pathlib import Path

from nemotron_copilot import Copilot, PatientPrediction

record = json.loads(Path("examples/mock_predictions.jsonl").read_text().splitlines()[0])
patient = PatientPrediction.from_dict(record)

copilot = Copilot(backend="mock")
result = copilot.interpret(patient)
print(result["narrative"])
```

For actual inference, replace the constructor with an explicit local snapshot:

```python
copilot = Copilot(backend="vllm", model_path=".cache/model-snapshot")
```

Create the instance once per process so weights stay loaded. `copilot.interpret(record)` also accepts a dictionary; `copilot.interpret_many(records)` accepts a list and returns results in the input order. Malformed inputs raise `ContractError`. Model initialization or runtime errors propagate; the vLLM backend does not silently become mock. The deterministic fallback handles generated text rejected by the narrative screen.

The compatibility function from the original proposal remains available:

```python
from nemotron_copilot import generate_clinical_narrative

narrative = generate_clinical_narrative(
    patient_id="P07",
    prob_mif=None,
    prob_clinical=0.66,
    prob_fused=None,
    top_features_mif=[],
    top_features_clinical=[],
    clinical_context="Synthetic clinical-only test case.",
    copilot=copilot,
)
```

Pass `None` for unavailable scores. This convenience function returns only text and uses default metadata; use the canonical record API when the UI needs thresholds, calibration, quality, and provenance.

## HTTP entry point for Junhao

Start a synthetic local service:

```bash
bash scripts/run_local.sh --command serve -- --host 127.0.0.1 --port 8000
```

On the HPC, use `bash run_hpc.sh --command serve --offline -- --host 127.0.0.1 --port 8000` to start the real model in an allocation. The service permits loopback binding. Connect from the same node or through a site-approved tunnel.

| Endpoint | Request |
| --- | --- |
| `GET /health` | No body; inspect service/backend state. |
| `POST /v1/interpret` | One canonical patient JSON object; returns one structured result. |
| `POST /v1/interpret-batch` | `{"patients": [record, ...]}`; returns `{"schema_version": "1.0", "results": [...]}` in the input order. |

Requests require `Content-Type: application/json` and a single `Content-Length` header. The maximum request body is 2,000,000 bytes; batches contain 1–128 unique patients. Chunked requests are not supported. Errors use `422` for malformed inputs, `413` for oversized bodies, `415` for the wrong content type, and `503` for local inference failure.

The model loads lazily on the first interpretation request. A healthy service with `model_loaded: false` has not yet verified a GPU model load; use the initial synthetic experiment to warm up and verify inference. For a browser UI on a different origin, call the copilot through the UI's server. This service does not configure cross-origin browser access.

```bash
curl --silent --show-error http://127.0.0.1:8000/health

curl --silent --show-error \
  -H 'Content-Type: application/json' \
  --data '{"schema_version":"1.0","patient_id":"P07","predictions":{"clinical":{"probability":0.66}},"clinical_context":"Synthetic test case."}' \
  http://127.0.0.1:8000/v1/interpret
```

The UI can also read the completed `narratives.jsonl` directly, avoiding a live GPU service during a presentation.

## Structured result for the UI

The response and JSONL output include `schema_version`, `patient_id`, `predictions`, `top_features`, `response_definition`, `narrative`, `narrative_source`, `review_required`, `limitations`, `comparison`, `quality`, and `provenance`. Display text as text rather than executable HTML.

`comparison` includes missing modalities, the clinical/mIF score gap when both exist, a configurable gap threshold (default `0.20`), a score-disagreement flag, a threshold-disagreement flag, and classifications computed only from supplied thresholds. A gap cutoff is a presentation heuristic, not a clinically validated boundary.

| Field/value | UI interpretation |
| --- | --- |
| `narrative_source = "mock"` | Deterministic demonstration; no language model ran. |
| `narrative_source = "vllm"` | Text came from the local model and passed the implemented screen. |
| `narrative_source = "fallback"` | Model text failed the screen; a deterministic evidence summary replaced it. |
| `quality.status` | `"mock"`, `"passed"`, or `"fallback"`; show issues when present. |
| `review_required = true` | Always show human-review status. |
| `limitations` | Show these alongside the narrative, including missing modalities, unknown calibration, and performance-claim limits. |

Automated screening is heuristic and cannot certify clinical correctness. Keep the original prediction values visible so the narrative's numeric statements can be checked independently.
