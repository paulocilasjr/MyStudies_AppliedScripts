"""Optional tile evidence is paired and audited, never certified as response scores."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from icb_copilot.handoff import _read_source
from icb_copilot.handoff_tiles import FEATURES_FILE, PREDICTIONS_FILE, read_tile_tables
from icb_copilot.schema import ContractError


SOURCE = Path(__file__).resolve().parents[1] / "examples" / "paulo_handoff"


class HandoffTileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "predictions").mkdir()
        for relative in (PREDICTIONS_FILE, FEATURES_FILE):
            shutil.copy2(SOURCE / relative, self.root / relative)
        self.predictions = {row["Patient_id"]: {} for row in csv.DictReader(
            (SOURCE / "predictions/patient_predictions.csv").read_text(encoding="utf-8").splitlines())}
        self.sources = []

    def read(self):
        return read_tile_tables(self.root, self.predictions, self.sources, _read_source)

    def change(self, relative, mutation):
        path = self.root / relative
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        mutation(fields, rows)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_current_packet_reports_347_attention_values_and_exact_unchanged_sources(self):
        before = {relative: (self.root / relative).read_bytes() for relative in (PREDICTIONS_FILE, FEATURES_FILE)}
        result = self.read()
        report = result["report"]
        self.assertTrue(report["present"])
        self.assertEqual(report["paired_rows"], 347)
        self.assertEqual(report["prediction_rows"], 347)
        self.assertEqual(report["feature_rows"], 347)
        self.assertEqual(report["feature_count"], 10)
        self.assertEqual(report["identical_value_count"], 347)
        self.assertTrue(report["all_tile_prob_equals_attention"])
        self.assertEqual(report["tile_prob_semantics"], "attention_weight")
        self.assertFalse(report["response_probabilities_verified"])
        self.assertEqual(report["missing_patient_ids"], [])
        self.assertEqual({pid: item["row_count"] for pid, item in report["patients"].items()},
                         {"S01": 85, "S02": 15, "S03": 130, "S04": 22, "S05": 95})
        self.assertAlmostEqual(report["patients"]["S01"]["attention_sum"], 0.999995)
        for item in result["raw_files"]:
            content = before[item["relative_path"]]
            self.assertEqual(item["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(item["size_bytes"], len(content))
            self.assertEqual((self.root / item["relative_path"]).read_bytes(), content)
            self.assertEqual(set(item), {"relative_path", "sha256", "size_bytes"})
        self.assertEqual(result["raw_files"], self.sources)
        json.dumps(result, allow_nan=False)

    def test_both_absent_is_backward_compatible_but_one_absent_fails(self):
        (self.root / PREDICTIONS_FILE).unlink()
        with self.assertRaisesRegex(ContractError, "both be present or both absent"):
            self.read()
        (self.root / FEATURES_FILE).unlink()
        result = self.read()
        self.assertFalse(result["report"]["present"])
        self.assertEqual(result["report"]["status"], "absent")
        self.assertEqual(result["raw_files"], [])

    def test_row_order_does_not_define_tile_correspondence(self):
        self.change(FEATURES_FILE, lambda fields, rows: rows.reverse())
        self.assertEqual(self.read()["report"]["identical_value_count"], 347)

    def test_different_values_mean_unknown_semantics_not_response_probabilities(self):
        self.change(PREDICTIONS_FILE, lambda fields, rows: rows[0].update(tile_prob="0.75"))
        report = self.read()["report"]
        self.assertEqual(report["identical_value_count"], 346)
        self.assertFalse(report["all_tile_prob_equals_attention"])
        self.assertEqual(report["tile_prob_semantics"], "unknown")
        self.assertFalse(report["response_probabilities_verified"])
        self.assertTrue(any("inequality does not establish" in warning for warning in report["warnings"]))

    def test_identity_audit_does_not_round_distinct_decimal_source_values(self):
        self.change(PREDICTIONS_FILE, lambda fields, rows: rows[0].update(tile_prob="0.00717600000000000000001"))
        self.assertEqual(self.read()["report"]["identical_value_count"], 346)

    def test_unmatched_or_extra_coordinates_fail_without_row_imputation(self):
        self.change(FEATURES_FILE, lambda fields, rows: rows[0].update(tile_x="1000"))
        with self.assertRaisesRegex(ContractError, "same patient/coordinate rows"):
            self.read()

    def test_duplicate_coordinates_and_ambiguous_slides_are_rejected(self):
        self.change(PREDICTIONS_FILE, lambda fields, rows: rows.append(dict(rows[0], slide_id="B")))
        with self.assertRaisesRegex(ContractError, "duplicate or ambiguous"):
            self.read()

    def test_duplicate_tile_ids_are_rejected(self):
        self.change(FEATURES_FILE, lambda fields, rows: rows[1].update(tile_id=rows[0]["tile_id"]))
        with self.assertRaisesRegex(ContractError, "duplicate tile_id"):
            self.read()

    def test_unknown_patients_and_invalid_identifiers_are_rejected(self):
        for value in ("OTHER", " S01", "S01\n"):
            with self.subTest(value=value):
                path = self.root / PREDICTIONS_FILE
                original = path.read_bytes()
                self.change(PREDICTIONS_FILE, lambda fields, rows: rows[0].update(Patient_id=value))
                with self.assertRaises(ContractError):
                    self.read()
                path.write_bytes(original)

    def test_known_patients_without_tiles_are_reported_without_fake_rows(self):
        self.predictions["S06"] = {}
        report = self.read()["report"]
        self.assertEqual(report["paired_rows"], 347)
        self.assertEqual(report["missing_patient_ids"], ["S06"])
        self.assertEqual(report["patients"]["S06"]["row_count"], 0)

    def test_nonfinite_or_out_of_range_values_and_negative_coordinates_fail(self):
        for relative, field, value in (
            (PREDICTIONS_FILE, "tile_prob", "nan"), (PREDICTIONS_FILE, "tile_prob", "1.1"),
            (FEATURES_FILE, "attention", "inf"), (FEATURES_FILE, "attention", "-0.01"),
            (FEATURES_FILE, "biopsy_skin", "1e999"), (FEATURES_FILE, "tile_x", "-1"),
            (PREDICTIONS_FILE, "tile_y", "NaN"),
        ):
            with self.subTest(relative=relative, field=field, value=value):
                path = self.root / relative
                original = path.read_bytes()
                self.change(relative, lambda fields, rows: rows[0].update({field: value}))
                with self.assertRaises(ContractError):
                    self.read()
                path.write_bytes(original)

    def test_feature_headers_require_ten_unique_columns(self):
        self.change(FEATURES_FILE, lambda fields, rows: (fields.append("extra"), [row.update(extra="0") for row in rows]))
        with self.assertRaisesRegex(ContractError, "exactly 10 feature columns"):
            self.read()
        original = (SOURCE / FEATURES_FILE).read_text(encoding="utf-8")
        self.root.joinpath(FEATURES_FILE).write_text(original.replace("biopsy_skin,biopsy_ln", "biopsy_skin,biopsy_skin", 1))
        with self.assertRaisesRegex(ContractError, "unique CSV headers"):
            self.read()

    def test_malformed_or_empty_csv_is_rejected(self):
        path = self.root / FEATURES_FILE
        content = path.read_text(encoding="utf-8")
        for broken in (content.splitlines()[0] + "\n", content + "S01,extra\n", '"unterminated'):
            with self.subTest(broken=broken[-25:]):
                path.write_text(broken, encoding="utf-8")
                with self.assertRaises(ContractError):
                    self.read()

    def test_source_reader_rejects_symlinked_optional_files(self):
        path = self.root / PREDICTIONS_FILE
        path.unlink()
        path.symlink_to(SOURCE / PREDICTIONS_FILE)
        with self.assertRaisesRegex(ContractError, "symlinks"):
            self.read()


if __name__ == "__main__":
    unittest.main()
