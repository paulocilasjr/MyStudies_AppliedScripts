"""Synthetic packet imports preserve evidence while exposing contradictions."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from icb_copilot.handoff import _clinical_figure_audit, canonical_jsonl_bytes, prepare_handoff, read_handoff
from icb_copilot.schema import ContractError

SOURCE = Path(__file__).resolve().parents[1] / "examples" / "paulo_handoff"


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "packet"
        shutil.copytree(SOURCE, self.source)

    def json_file(self, name):
        return self.source / "predictions" / name

    def mutate_json(self, name, mutation):
        path = self.json_file(name)
        data = json.loads(path.read_text(encoding="utf-8"))
        mutation(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def mutate_csv(self, mutation):
        path = self.json_file("patient_predictions.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            header, rows = reader.fieldnames, list(reader)
        mutation(rows)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

    def test_scores_labels_and_measurements_are_preserved_with_checked_source_shap(self):
        dataset = read_handoff(self.source)
        self.assertEqual([p["patient_id"] for p in dataset["patients"]], ["S01", "S02", "S03", "S04", "S05"])
        self.assertEqual(len(dataset["assets"]), 20)
        expected = [(0.9708, 0.8706, 0.9956, 1), (0.0734, 0.1055, 0.0093, 0),
                    (0.1142, 0.7966, 0.3355, 1), (0.9643, 0.1376, 0.8116, 1), (0.5824, 0.8955, 0.9228, 0)]
        for patient, (clinical, mif, fused, label) in zip(dataset["patients"], expected):
            self.assertEqual([patient["predictions"][m]["probability"] for m in ("clinical", "mif", "fused")], [clinical, mif, fused])
            self.assertEqual(patient["ground_truth"], label)
            self.assertEqual(patient["evaluation_partition"], "synthetic")
            self.assertEqual(patient["response_definition"], "Not specified")
            for prediction in patient["predictions"].values():
                self.assertEqual(prediction["decision_threshold"], 0.5)
                self.assertEqual(prediction["calibration"], "unknown")
            self.assertTrue(all(feature["attribution"] is None for feature in patient["top_features"]["mif"]))
            for feature, original in zip(patient["top_features"]["clinical"], dataset["original_analysis"][patient["patient_id"]]["clinical"]["features"]):
                self.assertEqual(feature["attribution"], {"method": "SHAP", "value": original["shap"], "scale": "responder_probability"})
            self.assertNotIn("Placeholder", patient["clinical_context"])
            self.assertNotIn("false positive", patient["clinical_context"])
            self.assertNotIn("AUC", patient["clinical_context"])
            self.assertIn("producer reports trained-model outputs", patient["clinical_context"])
            self.assertIn("source-declared", patient["clinical_context"])
            self.assertIn("linkage to the CSV mIF score is unresolved", patient["clinical_context"])
        self.assertIn("high-minus-low attention feature contrast=-17.3268", dataset["patients"][0]["top_features"]["mif"][0]["direction"])
        self.assertEqual(dataset["original_analysis"]["S01"]["clinical"]["features"][2]["value"], 1)
        self.assertEqual(dataset["original_analysis"]["S01"]["clinical"]["features"][0]["shap"], 0.2105)
        self.assertEqual(dataset["global_importance"]["clinical"][0]["importance"], 0.22)

    def test_v3_structured_shap_and_observed_plot_labels_match_with_explicit_rounding(self):
        dataset = read_handoff(self.source)
        self.assertEqual(dataset["report"]["clinical_shap_mismatch_count"], 0)
        self.assertEqual(dataset["report"]["clinical_shap_imported_count"], 5)
        self.assertEqual(dataset["report"]["clinical_plot_mismatch_count"], 0)
        outputs = [0.9708, 0.0734, 0.1142, 0.9643, 0.5824]
        for index, audit in enumerate(dataset["report"]["patients"].values()):
            self.assertEqual(audit["clinical_shap"]["output_value"], outputs[index])
            self.assertTrue(audit["clinical_shap"]["additivity_matches"])
            self.assertTrue(audit["clinical_shap"]["output_matches_prediction"])
            self.assertTrue(audit["clinical_shap"]["attributions_imported"])
            self.assertAlmostEqual(audit["clinical_shap"]["additivity_tolerance"], 7 * 0.00005)
            self.assertFalse(audit["clinical_shap"]["provenance_independently_validated"])
            self.assertTrue(audit["clinical_figure"]["manual_png_audit"])
            self.assertFalse(audit["clinical_figure"]["mismatch_detected"])
            self.assertTrue(audit["fusion"]["rounding_compatible"])
            self.assertTrue(audit["fusion"]["supplied_score_preserved"])
            self.assertTrue(any("source-declared" in warning for warning in audit["warnings"]))
        self.assertFalse(dataset["report"]["patients"]["S01"]["clinical_shap"]["exact_additivity_matches"])
        self.assertFalse(dataset["report"]["patients"]["S01"]["fusion"]["rounded_4dp_matches"])
        self.assertFalse(dataset["report"]["patients"]["S04"]["fusion"]["rounded_4dp_matches"])

    def test_optional_alternate_mif_score_is_audited_without_replacing_csv(self):
        dataset = read_handoff(self.source)
        self.assertEqual(dataset["report"]["mif_score_mismatch_count"], 0)
        for audit in dataset["report"]["patients"].values():
            self.assertIsNone(audit["mif_score"]["prob_mif_real"])
            self.assertIsNone(audit["mif_score"]["matches_csv"])
        expected = [0.9402, 0.7570, 0.9857, 0.9909, 0.9942]
        def add_alternate_scores(data):
            for record, alternate in zip(data.values(), expected):
                record["prob_mif_real"] = alternate
        self.mutate_json("patient_feature_analysis.json", add_alternate_scores)
        dataset = read_handoff(self.source)
        self.assertEqual(dataset["report"]["mif_score_mismatch_count"], 5)
        for patient, alternate in zip(dataset["patients"], expected):
            audit = dataset["report"]["patients"][patient["patient_id"]]["mif_score"]
            self.assertEqual(audit["prob_mif_real"], alternate)
            self.assertEqual(audit["csv_probability"], patient["predictions"]["mif"]["probability"])
            self.assertFalse(audit["matches_csv"])
            self.assertFalse(audit["explanation_linkage_resolved"])
        self.mutate_json("patient_feature_analysis.json", lambda data: data["S01"].update(prob_mif_real=1.2))
        with self.assertRaises(ContractError):
            read_handoff(self.source)

    def test_shap_admission_has_a_bounded_rounding_tolerance_and_requires_matching_output(self):
        path = self.json_file("patient_feature_analysis.json")
        original = path.read_bytes()
        for error, admitted in ((0.00035, True), (0.00036, False)):
            path.write_bytes(original)
            def adjust(data):
                data["S03"]["clinical"]["features"][0]["shap"] += error
            self.mutate_json("patient_feature_analysis.json", adjust)
            dataset = read_handoff(self.source)
            audit = dataset["report"]["patients"]["S03"]["clinical_shap"]
            self.assertEqual(audit["attributions_imported"], admitted)
            self.assertEqual(dataset["patients"][2]["top_features"]["clinical"][0]["attribution"] is not None, admitted)
        path.write_bytes(original)
        self.mutate_json("patient_feature_analysis.json", lambda data: data["S03"]["clinical"].update(output_value=0.1143))
        dataset = read_handoff(self.source)
        audit = dataset["report"]["patients"]["S03"]["clinical_shap"]
        self.assertTrue(audit["additivity_matches"])
        self.assertFalse(audit["output_matches_prediction"])
        self.assertFalse(audit["attributions_imported"])

    def test_legacy_packet_without_alternate_scores_or_tiles_remains_supported(self):
        def legacy(data):
            for index, record in enumerate(data.values()):
                record.pop("prob_mif_real", None)
                record["mif"] = record["mif"][:5]
                record["clinical"]["base_value"] = 0.5
                record["clinical"]["output_value"] = [0.91, 0.05, 0.39, 0.96, 0.59][index]
                for feature in record["clinical"]["features"]:
                    feature["shap"] = 0
                record["clinical"]["features"][0]["shap"] = record["clinical"]["output_value"] - 0.5
        self.mutate_json("patient_feature_analysis.json", legacy)
        scores = [(0.91, 0.82, 0.9788), (0.08, 0.15, 0.0151), (0.96, 0.28, 0.9032),
                  (0.04, 0.92, 0.3239), (0.84, 0.74, 0.9373)]
        self.mutate_csv(lambda rows: [row.update(prob_mif=str(m), prob_clinical=str(c), prob_fused=str(f)) for row, (m, c, f) in zip(rows, scores)])
        self.json_file("tile_features.csv").unlink()
        self.json_file("tile_predictions.csv").unlink()
        (self.source / "HANDOFF_PAULO.md").write_text("synthetic patient data only; fabricated demonstration outputs")
        dataset = read_handoff(self.source)
        self.assertEqual(dataset["report"]["clinical_shap_mismatch_count"], 5)
        self.assertEqual(dataset["report"]["clinical_shap_imported_count"], 0)
        self.assertFalse(dataset["report"]["tile_audit"]["present"])
        self.assertEqual(dataset["tile_files"], [])
        for patient in dataset["patients"]:
            self.assertTrue(all(feature["attribution"] is None for feature in patient["top_features"]["clinical"]))

    def test_nonadditive_shap_or_fusion_formula_disagreement_is_reported_without_repair(self):
        self.mutate_json("patient_feature_analysis.json", lambda data: data["S01"]["clinical"].update(base_value=0.4))
        self.mutate_csv(lambda rows: rows[0].update(prob_fused="0.9"))
        dataset = read_handoff(self.source)
        audit = dataset["report"]["patients"]["S01"]
        self.assertFalse(audit["clinical_shap"]["additivity_matches"])
        self.assertFalse(audit["clinical_shap"]["attributions_imported"])
        self.assertFalse(audit["fusion"]["rounded_4dp_matches"])
        self.assertFalse(audit["fusion"]["rounding_compatible"])
        self.assertEqual(dataset["patients"][0]["predictions"]["fused"]["probability"], 0.9)
        self.assertEqual(dataset["original_analysis"]["S01"]["clinical"]["base_value"], 0.4)

    def test_known_manual_figure_findings_are_hash_conditional(self):
        dataset = read_handoff(self.source)
        for pid in ("S01", "S02", "S03", "S04", "S05"):
            audit = dataset["report"]["patients"][pid]["clinical_figure"]
            self.assertTrue(audit["manual_png_audit"])
            self.assertFalse(audit["mismatch_detected"])
        figure = self.source / "figures" / "clinical_shap" / "shap_waterfall_S01.png"
        figure.write_bytes(figure.read_bytes() + b"\n")
        changed = read_handoff(self.source)
        self.assertFalse(changed["report"]["patients"]["S01"]["clinical_figure"]["manual_png_audit"])
        self.assertIsNone(changed["report"]["patients"]["S01"]["clinical_figure"]["mismatch_detected"])
        self.assertFalse(any("Manual audit of this original PNG" in note for note in changed["report"]["patients"]["S01"]["warnings"]))
        self.assertTrue(any("not automatically validated" in note for note in changed["assets"][0]["warnings"]))

    def test_manual_observations_compare_current_data_without_stale_hardcoded_assertions(self):
        def match_plot(data):
            clinical = data["S01"]["clinical"]
            clinical.update(base_value=0.5, output_value=0.91)
            values = {"has_lung_mets": 0.18, "had_targeted_therapy": 0.11, "gender_male": 0.09,
                      "tissue_resection": 0.06, "met_stage": -0.03}
            for feature in clinical["features"]:
                feature["shap"] = values[feature["raw_feature"]]
                if feature["raw_feature"] == "met_stage":
                    feature["value"] = 2
        self.mutate_json("patient_feature_analysis.json", match_plot)
        self.mutate_csv(lambda rows: rows[0].update(prob_clinical="0.91"))
        dataset = read_handoff(self.source)
        audit = dataset["report"]["patients"]["S01"]["clinical_figure"]
        self.assertTrue(audit["manual_png_audit"])
        self.assertTrue(audit["mismatch_detected"])
        self.assertTrue(any("displayed output" in text for text in audit["mismatches"]))
        self.assertTrue(any("Manual audit of this original PNG" in note for note in dataset["report"]["patients"]["S01"]["warnings"]))
        # The retained v2 observations still match their original values, while
        # the corrected v3 image must flag those same values as inconsistent.
        original = _clinical_figure_audit(
            "13b38cf9f45cd66c2844889c394b646f595ca68f2f7d3091824361b6783bd2c2",
            dataset["original_analysis"]["S01"]["clinical"], 0.91)
        self.assertFalse(original["mismatch_detected"])
        self.assertEqual(original["mismatches"], [])

    def test_tile_tables_are_fingerprinted_and_audited_as_attention_not_response(self):
        dataset = read_handoff(self.source)
        self.assertTrue(dataset["report"]["tile_audit"]["present"])
        self.assertEqual({entry["relative_path"] for entry in dataset["tile_files"]},
                         {"predictions/tile_features.csv", "predictions/tile_predictions.csv"})
        for entry in dataset["tile_files"]:
            self.assertIn(entry, dataset["source_files"])

    def test_prepare_publishes_exact_reproducible_bytes_and_private_audit_sidecars(self):
        before = {p.relative_to(self.source): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.rglob("*") if p.is_file()}
        dataset = read_handoff(self.source)
        destination = self.root / "prepared"
        manifest = prepare_handoff(self.source, destination)
        content = (destination / "patients.jsonl").read_bytes()
        self.assertEqual(content, canonical_jsonl_bytes(dataset["patients"]))
        self.assertEqual(hashlib.sha256(content).hexdigest(), manifest["input_sha256"])
        self.assertEqual(manifest["input_sha256"], dataset["input_sha256"])
        self.assertEqual(set(p.name for p in destination.iterdir()), {"patients.jsonl", "handoff_manifest.json", "patient_assets.json"})
        asset_manifest = json.loads((destination / "patient_assets.json").read_text())
        self.assertEqual(set(asset_manifest), {"schema_version", "synthetic", "assets"})
        for asset in asset_manifest["assets"]:
            self.assertEqual(hashlib.sha256((self.source / asset["relative_path"]).read_bytes()).hexdigest(), asset["sha256"])
            self.assertEqual((self.source / asset["relative_path"]).stat().st_size, asset["size_bytes"])
        for name, digest in manifest["artifact_hashes"].items():
            self.assertEqual(hashlib.sha256((destination / name).read_bytes()).hexdigest(), digest)
        if os.name == "posix":
            self.assertEqual(destination.stat().st_mode & 0o777, 0o700)
            self.assertTrue(all(path.stat().st_mode & 0o777 == 0o600 for path in destination.iterdir()))
        after = {p.relative_to(self.source): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_existing_outputs_and_original_source_are_protected(self):
        output = self.root / "existing"
        output.mkdir()
        (output / "keep.txt").write_text("preserve")
        with self.assertRaises(ValueError):
            prepare_handoff(self.source, output)
        self.assertEqual((output / "keep.txt").read_text(), "preserve")
        with self.assertRaises(ValueError):
            prepare_handoff(self.source, self.source / "generated")
        self.assertFalse((self.source / "generated").exists())

    def test_duplicate_or_unsafe_patient_ids_are_rejected(self):
        for value in ("S01", "../S02", " S02", "=S02"):
            with self.subTest(value=value):
                self.mutate_csv(lambda rows: rows[1].update(Patient_id=value))
                with self.assertRaises(ContractError):
                    read_handoff(self.source)
                self.mutate_csv(lambda rows: rows[1].update(Patient_id="S02"))

    def test_analysis_and_placeholder_ids_must_match_predictions(self):
        for name in ("patient_feature_analysis.json", "narratives.json"):
            path = self.json_file(name)
            original = path.read_bytes()
            self.mutate_json(name, lambda data: data.pop("S05"))
            with self.assertRaises(ContractError):
                read_handoff(self.source)
            path.write_bytes(original)

    def test_nonfinite_scores_and_invalid_synthetic_labels_are_rejected(self):
        for key, value in (("prob_mif", "nan"), ("prob_clinical", "inf"), ("prob_fused", "1.1"),
                           ("prob_clinical", "-0.1"), ("actual_response", ""), ("actual_response", "true")):
            with self.subTest(key=key, value=value):
                path = self.json_file("patient_predictions.csv")
                original = path.read_bytes()
                self.mutate_csv(lambda rows: rows[0].update({key: value}))
                with self.assertRaises(ContractError):
                    read_handoff(self.source)
                path.write_bytes(original)

    def test_json_duplicate_keys_infinite_exponents_and_boolean_effects_are_rejected(self):
        path = self.json_file("patient_feature_analysis.json")
        original = path.read_text()
        path.write_text(original.replace('"base_value": 0.4998', '"base_value": 0.4998, "base_value": 0.4998', 1))
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        path.write_text(original.replace('"shap": 0.2105', '"shap": 1e500', 1))
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        path.write_text(original.replace('"shap": 0.2105', '"shap": true', 1))
        with self.assertRaises(ContractError):
            read_handoff(self.source)

    def test_duplicate_features_and_undeclared_schema_fields_are_rejected(self):
        path = self.json_file("patient_feature_analysis.json")
        original = path.read_bytes()
        self.mutate_json("patient_feature_analysis.json", lambda data: data["S01"]["mif"].__setitem__(1, copy.deepcopy(data["S01"]["mif"][0])))
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        path.write_bytes(original)
        self.mutate_json("patient_feature_analysis.json", lambda data: data["S01"].update(unexpected_path="../../outside"))
        with self.assertRaises(ContractError):
            read_handoff(self.source)

    def test_finite_individual_shap_values_cannot_overflow_reconstruction(self):
        def overflow(data):
            for feature in data["S01"]["clinical"]["features"]:
                feature["shap"] = 1e308
        self.mutate_json("patient_feature_analysis.json", overflow)
        with self.assertRaisesRegex(ContractError, "SHAP sum must be finite"):
            read_handoff(self.source)

    def test_missing_extra_bad_signature_and_symlink_assets_are_rejected(self):
        figure = self.source / "figures" / "clinical_shap" / "shap_waterfall_S01.png"
        original = figure.read_bytes()
        figure.unlink()
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        figure.write_bytes(b"not a png")
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        figure.write_bytes(original)
        extra = figure.with_name("shap_waterfall_OLD.png")
        extra.write_bytes(original)
        with self.assertRaises(ContractError):
            read_handoff(self.source)
        extra.unlink()
        target = self.root / "outside.png"
        target.write_bytes(original)
        figure.unlink()
        figure.symlink_to(target)
        with self.assertRaises(ContractError):
            read_handoff(self.source)

    def test_only_explicitly_synthetic_handoff_is_supported(self):
        (self.source / "HANDOFF_PAULO.md").write_text("An unrelated prediction export.")
        with self.assertRaises(ContractError):
            read_handoff(self.source)

    def test_duplicate_canonical_ids_are_not_serialized(self):
        patients = read_handoff(self.source)["patients"]
        with self.assertRaises(ContractError):
            canonical_jsonl_bytes([patients[0], patients[0]])


if __name__ == "__main__":
    unittest.main()
