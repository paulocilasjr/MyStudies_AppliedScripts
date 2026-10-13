"""Exploratory prediction comparison on matched held-out patients, not LLM grading."""
from __future__ import annotations

from collections import Counter

from .schema import MODALITIES, ContractError, PatientPrediction


def _metrics(rows: list[dict], modality: str) -> dict:
    labels = [r["ground_truth"] for r in rows]
    scores = [r["predictions"][modality]["probability"] for r in rows]
    positives = [p for p, label in zip(scores, labels) if label == 1]
    negatives = [p for p, label in zip(scores, labels) if label == 0]
    auc = (sum(1 if p > n else 0.5 if p == n else 0 for p in positives for n in negatives) /
           (len(positives) * len(negatives))) if positives and negatives else None
    classified = [(r["ground_truth"], int(r["predictions"][modality]["probability"] >= r["predictions"][modality]["decision_threshold"]))
                  for r in rows if r["predictions"][modality]["decision_threshold"] is not None]
    return {"n": len(rows), "n_responders": sum(labels), "auroc": auc,
            "brier_score": sum((p - y) ** 2 for p, y in zip(scores, labels)) / len(rows) if rows else None,
            "accuracy": sum(y == pred for y, pred in classified) / len(classified) if classified else None,
            "n_with_threshold": len(classified),
            "model_ids": sorted({r["predictions"][modality]["model_id"] for r in rows})}


def evaluate_predictions(patients: list[PatientPrediction | dict]) -> dict:
    groups = {}
    excluded = Counter()
    seen = set()
    for patient in patients:
        row = PatientPrediction.from_dict(patient.to_dict() if isinstance(patient, PatientPrediction) else patient).to_dict()
        if row["patient_id"] in seen:
            raise ContractError("evaluation contains duplicate patient IDs")
        seen.add(row["patient_id"])
        if row["ground_truth"] is None:
            excluded["no_ground_truth"] += 1
        elif row["evaluation_partition"] not in {"test", "out_of_fold"}:
            excluded["not_test_or_out_of_fold"] += 1
        elif row["response_definition"].lower() in {"not specified", "unspecified", "unknown"}:
            excluded["unspecified_endpoint"] += 1
        else:
            key = (row["evaluation_partition"], row["response_definition"])
            groups.setdefault(key, []).append(row)
    results = []
    for (partition, endpoint), rows in groups.items():
        paired = [r for r in rows if all(m in r["predictions"] for m in MODALITIES)]
        paired_metrics = {m: _metrics(paired, m) for m in MODALITIES}
        deltas = {}
        for metric in ("auroc", "brier_score"):
            fused = paired_metrics["fused"][metric]
            deltas[metric + "_fused_minus_single"] = {
                m: fused - paired_metrics[m][metric] if fused is not None and paired_metrics[m][metric] is not None else None
                for m in ("clinical", "mif")}
        results.append({"evaluation_partition": partition, "response_definition": endpoint,
                        "available_cohorts": {m: _metrics([r for r in rows if m in r["predictions"]], m) for m in MODALITIES},
                        "paired_all_modalities": {"n": len(paired), "metrics": paired_metrics, "deltas": deltas}})
    return {"groups": results, "excluded_counts": dict(excluded), "warnings": [
        "Only explicitly labeled test or out_of_fold records with a specified endpoint are evaluated; partitions and endpoints are kept separate.",
        "Compare modalities on paired_all_modalities, not their different available cohorts. Higher AUROC and lower Brier score are favorable.",
        "Small-cohort estimates are exploratory. No significance, clinical utility, calibration adequacy or better patient outcomes are established.",
        "Held-out status, endpoint consistency, fold construction and attribution validity are declared by upstream producers and must be verified.",
        "Multiple model IDs within a modality may represent fold-specific models or incompatible exports; review listed model IDs before pooling.",
        "Accuracy uses only supplied thresholds and can have a different denominator; use ranking/loss metrics for the paired comparison."]}
