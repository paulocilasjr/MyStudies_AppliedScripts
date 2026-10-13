"""Exercise the audited viewer handoff without requiring Streamlit dependencies."""
import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

from nemotron_copilot import Copilot
from icb_copilot.experiment import run_experiment
from icb_copilot.ui_export import export_ui_bundle, UI_COMMIT

from helpers import clinical_only, prediction


class UIExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.counter = 0

    def complete(self, patient_id="P48"):
        row = prediction(patient_id)
        for model in row["predictions"].values():
            model["decision_threshold"] = 0.5
        return row

    def make_run(self, rows=None, copilot=None):
        self.counter += 1
        source = self.root / f"input-{self.counter}.jsonl"
        source.write_text("".join(json.dumps(row) + "\n" for row in (rows or [self.complete()])), encoding="utf-8")
        run_dir = self.root / f"run-{self.counter}"
        run_experiment(source, run_dir, copilot or Copilot(backend="mock"))
        return source, run_dir, self.root / f"ui-{self.counter}"

    def records(self, path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def csv_rows(self, output):
        with (output / "patient_predictions.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, ["Patient_id", "prob_mif", "prob_clinical", "prob_fused", "actual_response"])
            return list(reader)

    def write_records(self, run, rows):
        (run / "narratives.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def test_complete_subset_maps_actual_ui_contract_without_inventing_missing_scores(self):
        source, run, output = self.make_run([self.complete("001"), clinical_only("P07"), self.complete("P12")])
        summary = export_ui_bundle(run, output)
        rows = self.csv_rows(output)
        self.assertEqual([row["Patient_id"] for row in rows], ["001", "P12"])
        self.assertEqual(float(rows[0]["prob_mif"]), 0.79)
        self.assertTrue(all(row["actual_response"] == "" for row in rows))
        self.assertEqual(summary["ui_commit"], UI_COMMIT)
        self.assertEqual(summary["excluded_patients"], [{"patient_id": "P07", "reason": "UI requires all three scores", "missing_modalities": ["mif", "fused"]}])
        texts = json.loads((output / "narratives.json").read_text())
        self.assertEqual(set(texts), {"001", "P12"})
        self.assertIn("mock (no language model executed)", texts["001"])
        self.assertIn("Producer-declared calibration: clinical=unknown", texts["001"])
        self.assertIn("Limitations:", texts["001"])
        self.assertEqual((output / "copilot_results.jsonl").read_bytes(), (run / "narratives.jsonl").read_bytes())
        self.assertEqual((output / "copilot_manifest.json").read_bytes(), (run / "manifest.json").read_bytes())
        self.assertFalse((output / "feature_importances.json").exists())
        self.assertFalse((output / "tile_predictions.csv").exists())
        self.assertEqual(output.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(path.stat().st_mode & 0o777 == 0o600 for path in output.iterdir()))

    def test_verified_input_restores_only_eligible_known_labels(self):
        rows = [self.complete(f"P{i}") for i in range(5)]
        for row in rows:
            row.update(ground_truth=1, evaluation_partition="test", response_definition="Synthetic endpoint for test fixture")
        rows[1]["ground_truth"] = 0
        rows[2]["ground_truth"] = None
        rows[3]["evaluation_partition"] = "train"
        rows[4]["response_definition"] = "Not specified"
        source, run, output = self.make_run(rows)
        summary = export_ui_bundle(run, output, canonical_input=source)
        self.assertEqual([r["actual_response"] for r in self.csv_rows(output)], ["1", "0", "", "", ""])
        self.assertEqual(summary["actual_response_count"], 2)
        self.assertEqual(summary["evaluation_group"], ["test", "Synthetic endpoint for test fixture"])
        self.assertEqual(len(summary["withheld_labels"]), 3)

    def test_changed_input_cannot_attach_labels_to_another_run(self):
        source, run, output = self.make_run()
        source.write_text(source.read_text() + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "input_sha256"):
            export_ui_bundle(run, output, canonical_input=source)
        self.assertFalse(output.exists())

    def test_fingerprint_matching_input_still_requires_matching_result_evidence(self):
        source, run, output = self.make_run()
        rows = self.records(run / "narratives.jsonl")
        rows[0]["clinical_context"] = "A different synthetic context."
        self.write_records(run, rows)
        with self.assertRaisesRegex(ValueError, "evidence does not match"):
            export_ui_bundle(run, output, canonical_input=source)
        self.assertFalse(output.exists())

    def test_ui_cannot_silently_impose_missing_or_different_thresholds(self):
        for threshold in (None, 0.4, 0.6):
            with self.subTest(threshold=threshold):
                patient = self.complete()
                patient["predictions"]["clinical"]["decision_threshold"] = threshold
                _, run, output = self.make_run([patient])
                with self.assertRaisesRegex(ValueError, "UI imposes threshold 0.5"):
                    export_ui_bundle(run, output)
                self.assertFalse(output.exists())

    def test_no_complete_patients_is_an_explicit_error(self):
        _, run, output = self.make_run([clinical_only()])
        with self.assertRaisesRegex(ValueError, "no patients have all three"):
            export_ui_bundle(run, output)
        self.assertFalse(output.exists())

    def test_malformed_result_metadata_is_rejected_before_publication(self):
        bad = [("quality", None), ("comparison", []), ("provenance", None), ("review_required", False), ("narrative_source", [])]
        for field, value in bad:
            with self.subTest(field=field):
                _, run, output = self.make_run()
                rows = self.records(run / "narratives.jsonl")
                rows[0][field] = value
                self.write_records(run, rows)
                with self.assertRaises(ValueError):
                    export_ui_bundle(run, output)
                self.assertFalse(output.exists())

    def test_stale_comparison_and_source_quality_disagreement_are_rejected(self):
        for field in ("class", "quality"):
            with self.subTest(field=field):
                _, run, output = self.make_run()
                rows = self.records(run / "narratives.jsonl")
                if field == "class":
                    rows[0]["comparison"]["predicted_classes"]["clinical"] = 0
                else:
                    rows[0]["quality"]["status"] = "passed"
                self.write_records(run, rows)
                with self.assertRaises(ValueError):
                    export_ui_bundle(run, output)
                self.assertFalse(output.exists())

    def test_numeric_prefix_and_review_sentence_corruption_are_rejected(self):
        for corruption in ("score", "review"):
            with self.subTest(corruption=corruption):
                _, run, output = self.make_run()
                rows = self.records(run / "narratives.jsonl")
                if corruption == "score":
                    rows[0]["narrative"] = rows[0]["narrative"].replace("clinical 0.850", "clinical 0.950")
                else:
                    rows[0]["narrative"] = rows[0]["narrative"].removesuffix("Research output requires independent clinical review and does not establish treatment benefit.")
                self.write_records(run, rows)
                with self.assertRaisesRegex(ValueError, "factual prefix or review sentence"):
                    export_ui_bundle(run, output)
                self.assertFalse(output.exists())

    def test_manifest_counts_and_backend_types_must_match(self):
        for field, value in (("patient_count", 2), ("source_counts", {"mock": 2}), ("backend", {"backend": []})):
            with self.subTest(field=field):
                _, run, output = self.make_run()
                manifest_path = run / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest[field] = value
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(ValueError):
                    export_ui_bundle(run, output)
                self.assertFalse(output.exists())

    def test_duplicate_result_ids_cannot_overwrite_displayed_narratives(self):
        _, run, output = self.make_run()
        rows = self.records(run / "narratives.jsonl")
        self.write_records(run, rows + copy.deepcopy(rows))
        with self.assertRaisesRegex(ValueError, "duplicate result"):
            export_ui_bundle(run, output)

    def test_ui_roc_cannot_pool_different_endpoint_or_partition_groups(self):
        for field in ("evaluation_partition", "response_definition"):
            with self.subTest(field=field):
                rows = [self.complete("P1"), self.complete("P2")]
                for row in rows:
                    row.update(ground_truth=1, evaluation_partition="test", response_definition="Synthetic endpoint A")
                rows[1][field] = "out_of_fold" if field == "evaluation_partition" else "Synthetic endpoint B"
                source, run, output = self.make_run(rows)
                with self.assertRaisesRegex(ValueError, "UI pools labeled patients"):
                    export_ui_bundle(run, output, canonical_input=source)
                self.assertFalse(output.exists())

    def test_fallback_remains_explicit_with_screen_issues(self):
        def rejected(conversations):
            return [json.dumps({"interpretation": "Response is guaranteed at 99% and treatment should be selected."})] * len(conversations)
        _, run, output = self.make_run(copilot=Copilot(backend="vllm", generator=rejected))
        summary = export_ui_bundle(run, output)
        text = json.loads((output / "narratives.json").read_text())["P48"]
        self.assertEqual(summary["source_counts"], {"fallback": 1})
        self.assertIn("fallback (injected test generator)", text)
        self.assertIn("quality: fallback", text)
        self.assertIn("Screen issues:", text)

    def test_full_precision_scores_remain_available_near_the_ui_threshold(self):
        patient = self.complete()
        patient["predictions"]["clinical"]["probability"] = 0.4996
        _, run, output = self.make_run([patient])
        export_ui_bundle(run, output)
        self.assertEqual(self.csv_rows(output)[0]["prob_clinical"], "0.4996")
        text = json.loads((output / "narratives.json").read_text())["P48"]
        self.assertIn("Full-precision supplied scores: clinical=0.4996", text)
        sidecar = self.records(output / "copilot_results.jsonl")[0]
        self.assertEqual(sidecar["comparison"]["predicted_classes"]["clinical"], 0)

    def test_incomplete_source_run_and_existing_export_are_preserved(self):
        _, run, output = self.make_run()
        (run / "metrics.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing artifacts"):
            export_ui_bundle(run, output)
        self.assertFalse(output.exists())
        _, run, output = self.make_run()
        output.mkdir()
        prior = output / "prior.txt"
        prior.write_text("Reviewed bundle", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "absent or empty"):
            export_ui_bundle(run, output)
        self.assertEqual(prior.read_text(), "Reviewed bundle")


if __name__ == "__main__":
    unittest.main()
