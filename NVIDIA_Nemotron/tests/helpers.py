"""Synthetic fixtures shared by the copilot tests; no patient data."""

import copy
import json


def prediction(patient_id="P48"):
    """Return a fresh, complete canonical multimodal model handoff."""
    return {
        "schema_version": "1.0",
        "patient_id": patient_id,
        "predictions": {
            "clinical": {
                "probability": 0.85,
                "model_id": "clinical-demo",
                "calibration": "unknown",
                "decision_threshold": None,
            },
            "mif": {
                "probability": 0.79,
                "model_id": "mif-demo",
                "calibration": "unknown",
                "decision_threshold": None,
            },
            "fused": {
                "probability": 0.82,
                "model_id": "fusion-demo",
                "calibration": "unknown",
                "decision_threshold": None,
            },
        },
        "top_features": {
            "clinical": [
                {
                    "feature": "LDH level",
                    "value": 389,
                    "unit": "U/L",
                    "direction": "elevated",
                    "attribution": None,
                }
            ],
            "mif": [
                {
                    "feature": "CD3+ CD8+ Ripley's L (20um)",
                    "value": 45.2,
                    "unit": "",
                    "direction": "high",
                    "attribution": None,
                }
            ],
        },
        "clinical_context": "Synthetic melanoma example for a research demo.",
        "ground_truth": None,
        "evaluation_partition": "unspecified",
        "response_definition": "ICB responder is the positive class.",
    }


def clinical_only(patient_id="P01"):
    result = copy.deepcopy(prediction(patient_id))
    result["predictions"] = {"clinical": result["predictions"]["clinical"]}
    result["top_features"] = {"clinical": result["top_features"]["clinical"]}
    return result


# Generated report parts that pass the screen for unthresholded synthetic cases
# such as prediction(): they claim no threshold side, hypothesis or number.
SAFE_SECTIONS = {
    "prediction_summary": "No responder thresholds were supplied, so the scores are not assigned to a side and give no strong hypothesis.",
    "clinical_interpretation": "No signed clinical attribution was supplied, so the clinical features cannot be assigned a direction.",
    "conclusion": "No strong hypothesis can be drawn without thresholds. Cautions: the scores are uncalibrated and the models come from small cohorts.",
}


def part_of(conversation):
    """Report part a focused conversation asks for, identified by its system prompt."""
    from icb_copilot.prompts import FIELD_PROMPTS
    return next(field for field, prompt in FIELD_PROMPTS.items() if conversation[0]["content"] == prompt)


def generator(**sections):
    """Injected generator answering each report-part conversation with SAFE_SECTIONS, overridable per part."""
    texts = {**SAFE_SECTIONS, **sections}
    return lambda conversations: [json.dumps({"text": texts[part_of(c)]}) for c in conversations]
