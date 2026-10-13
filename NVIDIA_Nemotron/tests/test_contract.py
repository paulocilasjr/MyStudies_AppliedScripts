"""Validate producer handoffs before any inference or artifact writing."""

import copy
import math
import unittest

from nemotron_copilot import PatientPrediction

from helpers import clinical_only, prediction


class PatientContractTests(unittest.TestCase):
    def test_valid_multimodal_round_trip(self):
        source = prediction()
        result = PatientPrediction.from_dict(source).to_dict()
        self.assertEqual(result["patient_id"], "P48")
        self.assertEqual(result["predictions"], source["predictions"])
        self.assertEqual(result["top_features"], source["top_features"])

    def test_clinical_only_remains_clinical_only(self):
        result = PatientPrediction.from_dict(clinical_only()).to_dict()
        self.assertEqual(set(result["predictions"]), {"clinical"})
        self.assertNotIn("fused", result["predictions"])

    def test_validation_does_not_modify_the_callers_input(self):
        source = prediction()
        original = copy.deepcopy(source)
        PatientPrediction.from_dict(source)
        self.assertEqual(source, original)

    def test_probabilities_reject_non_finite_out_of_range_and_non_numbers(self):
        invalid = [-0.01, 1.01, math.nan, math.inf, -math.inf, True, False, "0.8", None]
        for value in invalid:
            with self.subTest(probability=value):
                source = prediction()
                source["predictions"]["mif"]["probability"] = value
                with self.assertRaises(ValueError):
                    PatientPrediction.from_dict(source)

    def test_probability_boundaries_are_valid(self):
        for value in [0, 1, 0.0, 1.0]:
            with self.subTest(probability=value):
                source = prediction()
                source["predictions"]["mif"]["probability"] = value
                self.assertEqual(
                    PatientPrediction.from_dict(source).to_dict()["predictions"]["mif"]["probability"],
                    value,
                )

    def test_patient_id_must_be_a_nonempty_string(self):
        for patient_id in [None, "", "  ", 48, True]:
            with self.subTest(patient_id=patient_id):
                with self.assertRaises(ValueError):
                    PatientPrediction.from_dict(prediction(patient_id))

    def test_at_least_one_model_prediction_is_required(self):
        source = prediction()
        source["predictions"] = {}
        with self.assertRaises(ValueError):
            PatientPrediction.from_dict(source)

    def test_threshold_has_the_same_numeric_constraints_as_probability(self):
        for value in [-0.1, 1.1, math.nan, True, "0.5"]:
            with self.subTest(decision_threshold=value):
                source = prediction()
                source["predictions"]["clinical"]["decision_threshold"] = value
                with self.assertRaises(ValueError):
                    PatientPrediction.from_dict(source)

    def test_observed_feature_direction_is_distinct_from_model_attribution(self):
        source = prediction()
        source["top_features"]["clinical"][0]["direction"] = "elevated"
        attribution = {"method": "SHAP", "value": -0.17, "scale": "log_odds"}
        source["top_features"]["clinical"][0]["attribution"] = attribution
        feature = PatientPrediction.from_dict(source).to_dict()["top_features"]["clinical"][0]
        self.assertEqual(feature["direction"], "elevated")
        self.assertEqual(feature["attribution"], attribution)

    def test_bad_metadata_types_raise_a_contract_error(self):
        for field, value in [("evaluation_partition", []), ("evaluation_partition", {}), ("schema_version", None)]:
            with self.subTest(field=field, value=value):
                source = prediction()
                source[field] = value
                with self.assertRaises(ValueError):
                    PatientPrediction.from_dict(source)
        source = prediction()
        source["predictions"]["clinical"]["calibration"] = []
        with self.assertRaises(ValueError):
            PatientPrediction.from_dict(source)


if __name__ == "__main__":
    unittest.main()
