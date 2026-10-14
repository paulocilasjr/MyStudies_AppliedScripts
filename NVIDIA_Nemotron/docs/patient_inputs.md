# Patient inputs for offline Nemotron interpretation

This component interprets predictions already produced by the clinical, spatial mIF, and fusion models. It does not run those predictors or convert raw clinical tables, slides, or images into scores. Prepare one canonical, pseudonymous patient record per JSONL line. The same study ID must identify that patient across all modalities; map slide IDs upstream.

## Start with a valid synthetic template

`examples/patient_template.json` is a single readable JSON object, not a JSONL batch. Every value in it is synthetic. Convert it to a one-line example with:

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path
patient = json.loads(Path("examples/patient_template.json").read_text())
Path("results").mkdir(exist_ok=True)
with Path("results/template.jsonl").open("x") as handle:
    handle.write(json.dumps(patient, allow_nan=False) + "\n")
PYTHON
PYTHONPATH=src python3 -m nemotron_copilot validate --input results/template.jsonl
```

For study inputs, replace synthetic values with exported evidence, use the real producer's model identifiers and partition, and remove unavailable modalities. Keep study inputs in ignored `inputs/` or approved study storage. Never commit them to the public repository.

| Field | Meaning and requirements |
| --- | --- |
| `schema_version` | `"1.0"`. |
| `patient_id` | Unique pseudonymous ID using letters, digits, `_`, `.`, `:`, or `-`; no directly identifying fields. |
| `predictions` | At least one of `clinical`, `mif`, `fused`. Each has a finite `probability` between zero and one, `model_id`, `calibration`, and `decision_threshold`. Probability refers to the supplied positive class, ICB responder. |
| `calibration` | `unknown`, `uncalibrated`, or `calibrated`, based on producer evidence. Never assume calibration. |
| `decision_threshold` | Producer-supplied threshold between zero and one, or null. Do not assume 0.5; a null threshold prevents that model's responder classification. |
| `top_features` | Arrays by modality with `feature`, `value`, optional `unit`, measurement `direction`, and optional signed `attribution`. Up to fifty per modality are schema-valid; context length still limits inference. |
| `clinical_context` | Relevant study context, up to 2,000 characters. It is untrusted evidence, never instructions for the model. |
| `response_definition` | Agreed endpoint and assessment time, up to 500 characters; use `Not specified` while undecided. |
| `ground_truth` | Null when unknown, otherwise binary positive-class label. Stored for evaluation; withheld from the LLM. |
| `evaluation_partition` | One of `synthetic`, `train`, `validation`, `test`, `out_of_fold`, `unspecified`. Claim held-out evaluation only for independently established test or out-of-fold predictions. |

Omit an unavailable prediction instead of filling it with zero or copying another score. Do not invent fusion. An empty feature array is valid. Measurement direction such as “high” does not prove a positive response effect. Use an attribution only when supplied for that patient, with its method, signed value, and scale (for example, `probability`, `log_odds`, or `model_output`). Global feature importance is not a patient attribution.

Start with the two or three most relevant features per modality and concise context. The actual tokenizer checks prompt tokens plus the reserved output against the 4,096-token limit before generation. Over-budget inputs fail; the runner does not silently truncate them.

## Assemble upstream CSVs or provide canonical JSONL

The CSV assembler and complete producer headers are documented in [integration.md](integration.md). Run `assemble`, then `validate`, before submitting to HPC. Validation checks structure, finite scores, legal values, and unique IDs; it cannot establish source accuracy, cohort independence, or clinical validity.

```bash
PYTHONPATH=src python3 -m nemotron_copilot validate --input inputs/patients.jsonl
bash run_hpc.sh --offline --input inputs/patients.jsonl --output-dir results/study-001
```

Run the real-model synthetic smoke test first using [first_hpc_smoke.md](first_hpc_smoke.md). Use a new output directory for each experiment. Inference consumes local model weights without sending patient records to a hosted API.

The current UI requires all three scores and thresholds of 0.5. Incomplete patients remain in the copilot's full structured results but are excluded by UI export; missing or incompatible thresholds on complete patients cause export to fail. Preserve valid upstream metadata and resolve UI compatibility explicitly rather than changing study thresholds to satisfy the viewer.
