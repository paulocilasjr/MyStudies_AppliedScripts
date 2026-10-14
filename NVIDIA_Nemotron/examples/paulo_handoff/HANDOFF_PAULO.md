# Handoff: Model Results for Demo UI Integration

**From:** Alyssa (DS1 — feature engineering + modeling)
**To:** Paulo (SE1 — Nemotron copilot + integration)
**Date:** October 13, 2026

---

## Quick Start

The zip file `paulo_handoff.zip` contains **synthetic patient data only** — safe
to use anywhere with no risk of real patient data leakage.

Copy the contents of the `predictions/` folder into Junhao's UI at
`results/predictions/` and select **Local output files** in the Streamlit app.

```
paulo_handoff.zip
├── predictions/
│   ├── patient_predictions.csv           # 5 synthetic patients (S01-S05)
│   ├── patient_feature_analysis.json     # Per-patient SHAP + mIF contrast
│   ├── feature_importances.json          # Global feature importance
│   └── narratives.json                   # Placeholder narratives (Paulo fills in)
├── figures/
│   ├── clinical_shap/                    # SHAP waterfall plots per patient
│   │   ├── shap_waterfall_S01.{png,pdf}
│   │   └── ...
│   └── mif_features/                     # mIF attention-contrast plots per patient
│       ├── mif_contrast_S01.{png,pdf}
│       └── ...
└── HANDOFF_PAULO.md                      # This document
```

---

## Synthetic Patients (S01-S05)

**All patient data in this zip is synthetic.** Tile features are simulated, but all
scores, SHAP values, attention weights, and feature contrasts are computed by the
real trained models (XGBoost and MIL) on the synthetic inputs. No real patient data
is included. Our collaborator does not want real patient data shared outside Moffitt.

| ID | Scenario | prob_mif | prob_clinical | prob_fused | Response |
|---|---|---|---|---|---|
| S01 | Models agree: responder | 0.87 | 0.97 | 1.00 | 1 |
| S02 | Models agree: non-responder | 0.09 | 0.07 | 0.01 | 0 |
| S03 | mIF high, clinical low | 0.80 | 0.11 | 0.34 | 1 |
| S04 | Clinical high, mIF low | 0.14 | 0.96 | 0.81 | 1 |
| S05 | False positive | 0.90 | 0.58 | 0.92 | 0 |

These cover the key demo scenarios: model agreement (S01, S02), modality
disagreement (S03, S04), and incorrect prediction (S05).

---

## Real Model Performance (aggregate, safe to share)

| Model | Type | Features | AUC (5-fold CV × 10 seeds) |
|---|---|---|---|
| **mIF MIL** | Gated attention MIL (~1500 params) | 7 spatial/compositional + 3 biopsy site | 0.81 ± 0.03 |
| **Clinical** | XGBoost (100 trees, depth 5) | 5 clinical features | 0.77 ± 0.04 |
| **Fusion** | Bayesian product rule (0 params) | Combines above | **0.88 ± 0.03** |

27 patients, CD8 ≥ 0.01 filter. These are aggregate statistics from real data.

---

## File Formats

### patient_predictions.csv

```csv
Patient_id,prob_mif,prob_clinical,prob_fused,actual_response
S01,0.8706,0.9708,0.9956,1
S02,0.0933,0.0734,0.0081,0
```

- 5 synthetic patients, matches Junhao's UI data contract
- `prob_fused` = Bayesian product rule: `(p_mif × p_clin) / (p_mif × p_clin + (1-p_mif)(1-p_clin))`
- `actual_response`: 1 = responder, 0 = non-responder

### patient_feature_analysis.json

Per-patient feature explanations for both modalities. Structure:

```json
{
  "S01": {
    "clinical": {
      "base_value": 0.50,
      "output_value": 0.97,
      "features": [
        {"feature": "Lung metastases", "raw_feature": "has_lung_mets",
         "value": 1, "shap": 0.2105},
        ...
      ]
    },
    "mif": [
      {"feature": "T cell → iNOS+ tumor proximity",
       "raw_feature": "ripleysL_20um.CD3+_to_iNOS+ SOX10+",
       "value": 38.2, "contrast": 22.5},
      ...
    ]
  }
}
```

**Clinical (SHAP waterfall):**
- `base_value`: Model's average prediction (E[f(x)] = 0.50, balanced classes)
- `output_value`: This patient's predicted P(response)
- `shap`: SHAP contribution of each feature (positive = pushes toward responder)
- `base_value + sum(shap) = output_value`
- Pre-rendered waterfall plots in `figures/clinical_shap/`

**mIF (attention contrast):**
- `value`: Attention-weighted mean of this feature across the patient's tiles
- `contrast`: Difference between high-attention tiles (≥75th pctl) and
  low-attention tiles (≤25th pctl). Positive = feature elevated in tiles
  the model focused on
- Pre-rendered bar charts in `figures/mif_features/`

### feature_importances.json

Global (not per-patient) feature importance for both modalities.
This is what Junhao's UI currently displays. Top features per modality.

### narratives.json

Placeholder — Paulo generates these with Nemotron. Keys must match Patient_id
values in patient_predictions.csv exactly (S01, S02, etc.).

### tile_predictions.csv (NOT INCLUDED)

We have tile-level attention weights but not tile-level response probabilities.
Can generate if needed for the spatial heatmap panel in Junhao's UI.

---

## Model Details for Nemotron Prompt

### mIF Model (Attention-based Multiple Instance Learning)
- Input: Per-patient "bag" of 1mm tissue tiles from multiplexed immunofluorescence
- Each tile has 10 features: 7 selected by univariate Mann-Whitney U ranking
  (from 268 deduplicated spatial/compositional candidates) + 3 biopsy site indicators
- Gated attention mechanism learns which tiles are most informative
- ~1500 trainable parameters
- CD8 ≥ 0.01 filter: only "immune-high" patients (27 of 29 mIF patients)

**Top mIF features (by attention correlation):**
1. T cell → iNOS+ tumor cell proximity (Ripley's L, 20μm)
2. B/T cell → CD8+ T cell co-localization (Ripley's L, 20μm)
3. T cell → B/T cell co-localization (Ripley's L, 20μm)
4. nNOS+/SOX10+ tumor subpopulation proportion
5. Cytotoxic T cell → PDL1+ cell proximity (Ripley's L, 20μm)

### Clinical Model (XGBoost)
- Input: 5 clinical features per patient (selected from 24 candidates)
- Trained on all 48 patients with clinical data; evaluated on 27 mIF-overlapping patients
- 100 trees, max depth 5, balanced class weights

**Clinical features (ranked by univariate significance):**
1. Lung metastases present (binary)
2. Prior targeted therapy — e.g., BRAF inhibitor (binary)
3. Metastatic stage — M1a/b/c (ordinal 1-3)
4. Gender male (binary)
5. Tissue resection vs core biopsy (binary)

### Fusion (Bayesian Product Rule)
- Parameter-free: no training required
- Treats mIF and clinical models as independent likelihood estimators
- Formula: P(R|mIF,clin) = (p_mif × p_clin) / (p_mif × p_clin + (1-p_mif)(1-p_clin))
- Equivalent to multiplying likelihood ratios under conditional independence

---

## Prompt Template Suggestion for Nemotron

The `patient_feature_analysis.json` provides everything needed to generate
per-patient narratives. Example prompt:

```
You are a clinical research assistant interpreting multimodal melanoma ICB
response predictions. Given a patient's model scores and feature explanations,
generate a concise clinical narrative.

Patient {patient_id}:
- mIF spatial model score: {prob_mif:.2f} ({"high" if prob_mif > 0.5 else "low"} probability of response)
- Clinical model score: {prob_clinical:.2f} ({"high" if prob_clinical > 0.5 else "low"} probability of response)
- Fused score: {prob_fused:.2f}
- Models {"agree" if (prob_mif > 0.5) == (prob_clinical > 0.5) else "disagree"}

Clinical features driving prediction (SHAP values, base=0.50):
{for each feature: "  {feature} = {value}: SHAP {shap:+.2f}"}

mIF spatial features (attention contrast, high vs low attention tiles):
{for each feature: "  {feature}: contrast {contrast:+.1f}"}

Generate a 2-3 sentence narrative explaining what the model scores suggest
about this patient's likely response to immune checkpoint blockade, noting
which modality contributes more and any discordance between models.
Do not make treatment recommendations.
```

---

## What's Coming Next

- **100-seed final run**: Currently at 10 seeds. Will run 100 seeds on HPC
  for tighter variance estimates.
- **Tile predictions**: Can generate if needed for the spatial heatmap panel.
- **Real patient SHAP/contrast**: Computed and cached at Moffitt for our
  own analysis (not shared externally).

---

## Junhao's UI Repository

https://github.com/qchiujunhao/melanoma-demo-ui

See `docs/DATA_CONTRACT.md` for exact file schemas.
See `docs/MOCK_INTEGRATION.md` for the verified mock workflow you already tested.
