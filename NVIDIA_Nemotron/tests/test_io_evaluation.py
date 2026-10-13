"""Protect patient joins and paired evaluation against misleading comparisons."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

from icb_copilot.evaluate import evaluate_predictions
from icb_copilot.io import assemble_predictions, load_jsonl

from helpers import clinical_only, prediction


class IngestionTests(unittest.TestCase):
    def write_csv(self, path, rows, headers=("patient_id", "probability")):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def test_join_is_by_patient_key_and_preserves_union_and_stable_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clinical = self.write_csv(root / "clinical.csv", [("P02", 0.2), ("P01", 0.9)])
            mif = self.write_csv(root / "mif.csv", [("P01", 0.8), ("P03", 0.7)])
            patients = [p.to_dict() for p in assemble_predictions(clinical_csv=clinical, mif_csv=mif)]
            self.assertEqual([p["patient_id"] for p in patients], ["P02", "P01", "P03"])
            self.assertEqual(set(patients[0]["predictions"]), {"clinical"})
            self.assertEqual(patients[1]["predictions"]["clinical"]["probability"], 0.9)
            self.assertEqual(patients[1]["predictions"]["mif"]["probability"], 0.8)
            self.assertEqual(set(patients[2]["predictions"]), {"mif"})
            self.assertTrue(all("fused" not in p["predictions"] for p in patients))

    def test_duplicate_csv_ids_are_rejected_instead_of_overwriting_patients(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(Path(directory) / "clinical.csv", [("P01", 0.2), ("P01", 0.9)])
            with self.assertRaisesRegex(ValueError, "duplicate.*ID"):
                assemble_predictions(clinical_csv=path)

    def test_invalid_column_counts_and_duplicate_headers_are_rejected(self):
        for headers, rows in [
            (("patient_id", "probability"), [("P01", 0.9, "extra")]),
            (("patient_id", "probability"), [("P01",)]),
            (("patient_id", "probability", "probability"), [("P01", 0.2, 0.9)]),
        ]:
            with self.subTest(headers=headers, rows=rows), tempfile.TemporaryDirectory() as directory:
                path = self.write_csv(Path(directory) / "invalid.csv", rows, headers)
                with self.assertRaises(ValueError):
                    assemble_predictions(clinical_csv=path)

    def test_context_is_attached_by_id_and_cannot_override_predictions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clinical = self.write_csv(root / "clinical.csv", [("P02", 0.2), ("P01", 0.9)])
            context = root / "context.jsonl"
            context.write_text(json.dumps({"patient_id": "P01", "clinical_context": "Synthetic context"}) + "\n")
            patients = [p.to_dict() for p in assemble_predictions(clinical_csv=clinical, context_jsonl=context)]
            self.assertEqual(patients[0]["clinical_context"], "")
            self.assertEqual(patients[1]["clinical_context"], "Synthetic context")
            context.write_text(json.dumps({"patient_id": "P01", "predictions": {"clinical": {"probability": 0.1}}}) + "\n")
            with self.assertRaises(ValueError):
                assemble_predictions(clinical_csv=clinical, context_jsonl=context)

    def test_unknown_or_duplicate_context_ids_fail_explicitly(self):
        for contexts in [
            [{"patient_id": "P99"}],
            [{"patient_id": "P01"}, {"patient_id": "P01"}],
        ]:
            with self.subTest(contexts=contexts), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                clinical = self.write_csv(root / "clinical.csv", [("P01", 0.9)])
                context = root / "context.jsonl"
                context.write_text("\n".join(map(json.dumps, contexts)) + "\n")
                with self.assertRaises(ValueError):
                    assemble_predictions(clinical_csv=clinical, context_jsonl=context)

    def test_jsonl_line_errors_are_actionable_and_nonfinite_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.jsonl"
            source = json.dumps(prediction()).replace('"probability": 0.85', '"probability": NaN')
            path.write_text("\n" + source + "\n")
            with self.assertRaisesRegex(ValueError, "line 2.*nonfinite"):
                load_jsonl(path)


class EvaluationTests(unittest.TestCase):
    def heldout(self, patient_id, label, probabilities, partition="test", endpoint="RECIST response at prespecified assessment"):
        patient = prediction(patient_id)
        patient.update(ground_truth=label, evaluation_partition=partition, response_definition=endpoint)
        for modality, probability in probabilities.items():
            patient["predictions"][modality].update(probability=probability, decision_threshold=0.5)
        return patient

    def test_deltas_use_paired_patients_rather_than_different_available_cohorts(self):
        positive = self.heldout("P01", 1, {"clinical": 0.9, "mif": 0.4, "fused": 0.8})
        negative = self.heldout("P02", 0, {"clinical": 0.95, "mif": 0.6, "fused": 0.2})
        extra = clinical_only("P03")
        extra.update(ground_truth=0, evaluation_partition="test", response_definition=positive["response_definition"])
        extra["predictions"]["clinical"]["probability"] = 0.1
        group = evaluate_predictions([positive, negative, extra])["groups"][0]
        self.assertEqual(group["available_cohorts"]["clinical"]["n"], 3)
        self.assertEqual(group["available_cohorts"]["clinical"]["auroc"], 0.5)
        paired = group["paired_all_modalities"]
        self.assertEqual(paired["n"], 2)
        self.assertEqual(paired["metrics"]["clinical"]["auroc"], 0)
        self.assertEqual(paired["metrics"]["fused"]["auroc"], 1)
        self.assertAlmostEqual(paired["metrics"]["fused"]["brier_score"], 0.04)
        self.assertEqual(paired["deltas"]["auroc_fused_minus_single"]["clinical"], 1)
        self.assertAlmostEqual(paired["deltas"]["brier_score_fused_minus_single"]["clinical"], -0.41625)

    def test_training_synthetic_unlabeled_and_unspecified_endpoint_are_excluded(self):
        unlabeled = prediction("P01")
        training = self.heldout("P02", 1, {}, partition="train")
        synthetic = self.heldout("P03", 0, {}, partition="synthetic")
        unspecified = self.heldout("P04", 1, {}, endpoint="Not specified")
        result = evaluate_predictions([unlabeled, training, synthetic, unspecified])
        self.assertEqual(result["groups"], [])
        self.assertEqual(result["excluded_counts"], {
            "no_ground_truth": 1, "not_test_or_out_of_fold": 2, "unspecified_endpoint": 1,
        })

    def test_endpoint_and_out_of_fold_partition_are_kept_separate(self):
        rows = [
            self.heldout("P01", 1, {}, partition="test", endpoint="Endpoint A"),
            self.heldout("P02", 0, {}, partition="out_of_fold", endpoint="Endpoint A"),
            self.heldout("P03", 1, {}, partition="test", endpoint="Endpoint B"),
        ]
        result = evaluate_predictions(rows)
        self.assertEqual(len(result["groups"]), 3)
        self.assertTrue(all(g["paired_all_modalities"]["n"] == 1 for g in result["groups"]))
        self.assertTrue(all(g["paired_all_modalities"]["metrics"]["fused"]["auroc"] is None for g in result["groups"]))

    def test_missing_threshold_does_not_default_accuracy_to_point_five(self):
        row = self.heldout("P01", 1, {})
        row["predictions"]["clinical"]["decision_threshold"] = None
        metrics = evaluate_predictions([row])["groups"][0]["available_cohorts"]["clinical"]
        self.assertIsNone(metrics["accuracy"])
        self.assertEqual(metrics["n_with_threshold"], 0)

    def test_duplicate_patients_cannot_inflate_evaluation_counts(self):
        row = self.heldout("P01", 1, {})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluate_predictions([row, row])


if __name__ == "__main__":
    unittest.main()
