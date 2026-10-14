"""Preserve the handoff's synthetic scenarios and explicitly flagged figures."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from icb_copilot.copilot import Copilot
from icb_copilot.experiment import run_experiment
from icb_copilot.handoff import prepare_handoff
from icb_copilot.handoff_export import export_handoff_bundle
from icb_copilot.ui_export import export_ui_bundle

PACKET = Path(__file__).resolve().parents[1] / "examples/paulo_handoff"


class HandoffExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.prepared = self.root / "input"
        prepare_handoff(PACKET, self.prepared)
        self.source = self.prepared / "patients.jsonl"
        self.run = self.root / "experiment"
        run_experiment(self.source, self.run, Copilot(backend="mock"))
        self.output = self.root / "ui"

    def test_complete_bundle_preserves_labels_plots_and_discloses_mismatches(self):
        summary = export_handoff_bundle(PACKET, self.run, self.output)
        self.assertEqual(summary["patient_count"], 5)
        self.assertEqual(summary["source_counts"], {"mock": 5})
        self.assertEqual(summary["figure_count"], 20)
        self.assertTrue(summary["synthetic_labels"])
        self.assertFalse(summary["placeholder_narratives_used"])
        with (self.output / "patient_predictions.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["Patient_id"] for row in rows], ["S01", "S02", "S03", "S04", "S05"])
        self.assertEqual([row["actual_response"] for row in rows], ["1", "0", "1", "1", "0"])
        self.assertEqual(float(rows[0]["prob_clinical"]), 0.9708)
        self.assertEqual(float(rows[0]["prob_fused"]), 0.9956)
        texts = json.loads((self.output / "narratives.json").read_text())
        for text in texts.values():
            self.assertNotIn("[Placeholder", text)
            self.assertIn("SYNTHETIC DEMONSTRATION", text)
            self.assertIn("mock (no language model executed)", text)
            self.assertIn("prob_mif_real", text)
            self.assertNotIn("scores and observed labels are fabricated", text)
        assets = json.loads((self.output / "patient_assets.json").read_text())["assets"]
        for asset in assets:
            target = self.output / asset["relative_path"]
            self.assertEqual(target.read_bytes(), (PACKET / asset["relative_path"]).read_bytes())
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), asset["sha256"])
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads((self.output / "patient_feature_analysis.json").read_text()),
                         json.loads((PACKET / "predictions/patient_feature_analysis.json").read_text()))
        report = json.loads((self.output / "handoff_manifest.json").read_text())
        self.assertEqual(report["clinical_shap_mismatch_count"], 0)
        self.assertTrue(all(audit["clinical_shap"]["attributions_imported"] for audit in report["patients"].values()))
        self.assertFalse((self.output / "tile_predictions.csv").exists())
        self.assertFalse(summary["tile_response_probabilities_exported"])
        self.assertEqual(len(summary["source_data"]), 2)
        for name in ("tile_predictions.csv", "tile_features.csv"):
            self.assertEqual((self.output / "source_data" / name).read_bytes(), (PACKET / "predictions" / name).read_bytes())
        self.assertTrue((self.output / "source_data" / "manifest.json").exists())
        self.assertEqual(json.loads((self.run / "metrics.json").read_text())["groups"], [])

    def test_changed_packet_cannot_attach_wrong_evidence_to_old_narratives(self):
        changed = self.root / "changed"
        shutil.copytree(PACKET, changed)
        path = changed / "predictions/patient_predictions.csv"
        path.write_text(path.read_text().replace("S01,0.8706,0.9708,", "S01,0.8706,0.81,"))
        with self.assertRaisesRegex(ValueError, "run input does not match"):
            export_handoff_bundle(changed, self.run, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_ui_bundle_is_preserved(self):
        self.output.mkdir()
        marker = self.output / "reviewed.txt"
        marker.write_text("preserve")
        with self.assertRaisesRegex(ValueError, "absent or empty"):
            export_handoff_bundle(PACKET, self.run, self.output)
        self.assertEqual(marker.read_text(), "preserve")

    def test_general_export_withholds_synthetic_labels_unless_explicitly_requested(self):
        export_ui_bundle(self.run, self.output, canonical_input=self.source)
        with (self.output / "patient_predictions.csv").open(newline="") as handle:
            self.assertTrue(all(row["actual_response"] == "" for row in csv.DictReader(handle)))
        with self.assertRaisesRegex(ValueError, "matching canonical input"):
            export_ui_bundle(self.run, self.root / "invalid", include_synthetic_labels=True)

    def test_synthetic_label_option_cannot_relabel_real_partitions(self):
        records = [json.loads(line) for line in self.source.read_text().splitlines()]
        records[0]["evaluation_partition"] = "test"
        changed = self.root / "mixed.jsonl"
        changed.write_text("".join(json.dumps(row) + "\n" for row in records))
        changed_run = self.root / "mixed-run"
        run_experiment(changed, changed_run, Copilot(backend="mock"))
        with self.assertRaisesRegex(ValueError, "every patient declared synthetic"):
            export_ui_bundle(changed_run, self.output, canonical_input=changed, include_synthetic_labels=True)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
