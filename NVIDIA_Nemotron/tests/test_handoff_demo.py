"""Exercise the synthetic file viewer, including an optional actual AppTest."""
import csv
from contextlib import nullcontext, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from icb_copilot.copilot import Copilot
from icb_copilot.handoff import read_handoff
from icb_copilot.server import create_server

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "demo" / "handoff_app.py"
SOURCE = ROOT / "examples" / "paulo_handoff"
spec = importlib.util.spec_from_file_location("handoff_app", APP)
viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)
HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None
HAS_PIL = importlib.util.find_spec("PIL") is not None


class HandoffDemoTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.bundle = Path(self.temporary.name) / "ui"
        self.bundle.mkdir()
        dataset = read_handoff(SOURCE)
        for name in ("patient_predictions.csv", "patient_feature_analysis.json", "feature_importances.json"):
            shutil.copyfile(SOURCE / "predictions" / name, self.bundle / name)
        shutil.copytree(SOURCE / "figures", self.bundle / "figures")
        results = Copilot(backend="mock").interpret_many(dataset["patients"])
        self.write_json("narratives.json", {r["patient_id"]: r["narrative"] for r in results})
        self.write_results(results)
        self.write_json("ui_export_manifest.json", {"schema_version": "1.0", "display_threshold": 0.5,
                                                   "synthetic_labels": True, "bundle_kind": "synthetic_paulo_handoff",
                                                   "included_patient_ids": [r["patient_id"] for r in results]})
        self.write_json("handoff_manifest.json", dataset["report"])
        self.write_json("patient_assets.json", {"schema_version": "1.0", "synthetic": True, "assets": dataset["assets"]})

    def write_json(self, name, obj):
        (self.bundle / name).write_text(json.dumps(obj), encoding="utf-8")

    def json(self, name):
        return json.loads((self.bundle / name).read_text(encoding="utf-8"))

    def results(self):
        return [json.loads(line) for line in (self.bundle / "copilot_results.jsonl").read_text().splitlines()]

    def write_results(self, results):
        (self.bundle / "copilot_results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results), encoding="utf-8")

    def nim_results_fixture(self):
        """Provider-result snapshot fixture for the viewer, with no network calls."""
        rows = self.results()
        for row in rows:
            row["narrative_source"] = "nim"
            row["quality"]["status"] = "passed"
            row["provenance"].pop("generator", None)
            row["provenance"].update(backend="nim", model={"model_id": "nvidia/nemotron-3-ultra-550b-a55b",
                                                           "revision": "provider-managed"})
        self.write_results(rows)
        return rows

    def test_nim_snapshot_loads_with_remote_source_and_model_identity(self):
        self.nim_results_fixture()
        loaded = viewer.load_bundle(self.bundle)
        for patient in loaded["patients"].values():
            label = viewer.source_text(patient["result"])
            self.assertIn("NVIDIA-hosted NIM generated text (remote inference)", label)
            self.assertIn("nvidia/nemotron-3-ultra-550b-a55b", label)
            self.assertIn("provider-managed", label)
            self.assertNotIn("Local", label)

    def test_nim_requires_matching_source_backend_model_and_quality(self):
        original = self.nim_results_fixture()
        for corruption in ("backend", "quality", "model", "revision", "issues"):
            with self.subTest(corruption=corruption):
                rows = json.loads(json.dumps(original))
                if corruption == "backend":
                    rows[0]["provenance"]["backend"] = "mock"
                elif corruption == "quality":
                    rows[0]["quality"]["status"] = "mock"
                elif corruption == "model":
                    del rows[0]["provenance"]["model"]
                elif corruption == "revision":
                    rows[0]["provenance"]["model"]["revision"] = "invented-local-revision"
                else:
                    rows[0]["quality"]["issues"] = ["Failed screening"]
                self.write_results(rows)
                with self.assertRaises(ValueError):
                    viewer.load_bundle(self.bundle)

    def test_nim_live_panel_describes_remote_backend_through_loopback_api(self):
        result = self.nim_results_fixture()[0]
        st = Mock()
        st.session_state = {}
        st.button.return_value = True
        st.spinner.return_value = nullcontext()
        with patch.object(viewer, "api_health", return_value={"backend": "nim", "model_loaded": False}), \
                patch.object(viewer, "live_interpret", return_value=result) as generate:
            viewer.live_panel(st, "http://127.0.0.1:8000", "S01", result)
        generate.assert_called_once_with("http://127.0.0.1:8000", result)
        caption = st.caption.call_args_list[0].args[0]
        self.assertIn("loopback copilot API", caption)
        self.assertIn("NVIDIA's hosted API", caption)
        self.assertIn("remote inference", caption)
        self.assertNotIn("model loaded", caption)
        self.assertIn("remotely", st.spinner.call_args.args[0])

    def test_standalone_html_retains_nim_identity_and_sanitized_provenance(self):
        rows = self.nim_results_fixture()
        rows[0]["provenance"]["model"]["local_path"] = "/private/machine-specific-model"
        rows[0]["provenance"]["settings"] = {"api_key": "secret-test-sentinel"}
        rows[1]["provenance"]["generator"] = "injected"
        self.write_results(rows)
        spec = importlib.util.spec_from_file_location("standalone_export", ROOT / "scripts/export_standalone_demo.py")
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        output = self.bundle.parent / "viewer.html"
        with redirect_stdout(io.StringIO()):
            exporter.export(self.bundle, output)
        html = output.read_text()
        payload = json.loads(html.split("const DATA = ", 1)[1].split(";\nconst $", 1)[0])
        self.assertEqual(len(payload["patients"]), 5)
        for patient in payload["patients"]:
            self.assertIn("NVIDIA-hosted NIM", patient["source_label"])
            self.assertEqual(patient["provenance"]["model"], {"model_id": "nvidia/nemotron-3-ultra-550b-a55b", "revision": "provider-managed"})
        self.assertNotIn("machine-specific-model", html)
        self.assertNotIn("secret-test-sentinel", html)
        self.assertIn("injected test generator", payload["patients"][1]["source_label"])
        self.assertEqual(payload["patients"][1]["provenance"]["generator"], "injected")

    def test_v3_cases_keep_scores_labels_and_remove_resolved_mismatch_warnings(self):
        loaded = viewer.load_bundle(self.bundle)
        self.assertEqual(list(loaded["patients"]), ["S01", "S02", "S03", "S04", "S05"])
        for patient in loaded["patients"].values():
            self.assertEqual(patient["result"]["narrative_source"], "mock")
            self.assertTrue(patient["result"]["review_required"])
            self.assertEqual(patient["analysis"]["clinical"]["output_value"], patient["scores"]["clinical"])
            self.assertFalse(patient["clinical_plot_mismatch"])
            self.assertIsNone(patient["mif_score"]["matches_csv"])
            self.assertIsNone(patient["mif_score"]["prob_mif_real"])
            self.assertEqual(set(patient["assets"]), {("clinical_shap", "png"), ("clinical_shap", "pdf"),
                                                       ("mif_contrast", "png"), ("mif_contrast", "pdf")})
        self.assertEqual(loaded["patients"]["S03"]["actual_response"], 1)
        self.assertEqual(loaded["patients"]["S05"]["actual_response"], 0)
        self.assertEqual(viewer.outcome_label(loaded["patients"]["S03"]["scores"]["fused"], 1), "False negative")
        self.assertEqual(viewer.outcome_label(loaded["patients"]["S04"]["scores"]["fused"], 1), "True positive")
        self.assertEqual(viewer.outcome_label(loaded["patients"]["S05"]["scores"]["fused"], 0), "False positive")
        for pid in loaded["patients"]:
            self.assertFalse(any("Manual audit" in text for text in loaded["patients"][pid]["warnings"]))

    def test_core_loader_imports_without_streamlit_or_gpu_packages(self):
        script = f"import runpy,sys; runpy.run_path({str(APP)!r},run_name='viewer_import'); assert not any(name in sys.modules for name in ('streamlit','torch','vllm','transformers'))"
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_live_api_url_must_be_plain_loopback_http(self):
        self.assertEqual(viewer.loopback_api("http://127.0.0.1:8000/"), "http://127.0.0.1:8000")
        self.assertEqual(viewer.loopback_api("http://localhost:8123"), "http://localhost:8123")
        for url in ("https://127.0.0.1:8000", "http://10.0.0.5:8000", "http://example.org:8000",
                    "http://127.0.0.1:8000/v1/interpret", "http://user@127.0.0.1:8000"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                viewer.loopback_api(url)

    def test_live_panel_requests_regenerate_supplied_evidence_without_labels(self):
        received = []
        copilot = Copilot(backend="mock")
        original = copilot.interpret
        copilot.interpret = lambda patient: received.append(patient) or original(patient)
        server = create_server(copilot, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 3)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        api = viewer.loopback_api(f"http://127.0.0.1:{server.server_address[1]}")
        self.assertEqual(viewer.api_health(api)["backend"], "mock")
        batch = self.results()[0]
        live = viewer.live_interpret(api, batch)
        self.assertEqual(set(received[0]), set(viewer.LIVE_FIELDS))
        self.assertEqual(live["narrative"], batch["narrative"])
        self.assertEqual(live["predictions"], batch["predictions"])

    def test_absolute_and_traversing_asset_paths_are_rejected(self):
        original = self.json("patient_assets.json")
        for path in ("../figures/out.png", "/tmp/out.png", "figures/../out.png", "figures\\out.png"):
            with self.subTest(path=path):
                changed = json.loads(json.dumps(original))
                changed["assets"][0]["relative_path"] = path
                self.write_json("patient_assets.json", changed)
                with self.assertRaises(ValueError):
                    viewer.load_bundle(self.bundle)

    def test_asset_symlink_escape_is_rejected_even_if_hash_matches(self):
        assets = self.json("patient_assets.json")
        entry = assets["assets"][0]
        image = self.bundle / entry["relative_path"]
        outside = self.bundle.parent / "outside.png"
        shutil.copyfile(image, outside)
        image.unlink()
        image.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "inside the bundle"):
            viewer.load_bundle(self.bundle)

    def test_changed_plot_is_not_displayed_under_an_old_asset_manifest(self):
        entry = self.json("patient_assets.json")["assets"][0]
        image = self.bundle / entry["relative_path"]
        content = image.read_bytes()
        image.write_bytes(content[:-1] + bytes([content[-1] ^ 1]))
        with self.assertRaisesRegex(ValueError, "SHA256"):
            viewer.load_bundle(self.bundle)

    def test_asset_ids_and_types_cannot_cross_patient_boundaries(self):
        original = self.json("patient_assets.json")
        for field, value in (("patient_id", "UNKNOWN"), ("patient_id", "../S01"), ("kind", "tile_response"), ("format", "svg")):
            with self.subTest(field=field, value=value):
                changed = json.loads(json.dumps(original))
                changed["assets"][0][field] = value
                self.write_json("patient_assets.json", changed)
                with self.assertRaises(ValueError):
                    viewer.load_bundle(self.bundle)

    def test_duplicate_assets_and_missing_pngs_fail_explicitly(self):
        original = self.json("patient_assets.json")
        for entries in (original["assets"] + [original["assets"][0]], original["assets"][1:]):
            self.write_json("patient_assets.json", {**original, "assets": entries})
            with self.assertRaises(ValueError):
                viewer.load_bundle(self.bundle)

    def test_csv_and_structured_scores_or_thresholds_must_match(self):
        original = self.results()
        for field, value in (("probability", 0.81), ("decision_threshold", None), ("probability", True), ("probability", "0.82")):
            with self.subTest(field=field, value=value):
                changed = json.loads(json.dumps(original))
                changed[0]["predictions"]["clinical"][field] = value
                self.write_results(changed)
                with self.assertRaises(ValueError):
                    viewer.load_bundle(self.bundle)

    def test_duplicate_or_unknown_copilot_result_ids_do_not_overwrite_narratives(self):
        original = self.results()
        for rows in (original + [original[0]], original[:-1]):
            self.write_results(rows)
            with self.assertRaises(ValueError):
                viewer.load_bundle(self.bundle)

    def test_mock_and_failed_generations_cannot_be_labeled_as_passed(self):
        rows = self.results()
        rows[0]["quality"]["status"] = "passed"
        self.write_results(rows)
        with self.assertRaisesRegex(ValueError, "source/quality/review"):
            viewer.load_bundle(self.bundle)

    def test_narrative_ids_and_synthetic_declaration_are_required(self):
        narratives = self.json("narratives.json")
        self.write_json("narratives.json", {**narratives, "UNKNOWN": "Unrelated text"})
        with self.assertRaisesRegex(ValueError, "exactly the supplied patient IDs"):
            viewer.load_bundle(self.bundle)
        self.write_json("narratives.json", narratives)
        manifest = self.json("handoff_manifest.json")
        self.write_json("handoff_manifest.json", {**manifest, "synthetic": False})
        with self.assertRaisesRegex(ValueError, "synthetic"):
            viewer.load_bundle(self.bundle)

    def test_ordinary_ui_exports_cannot_be_mistaken_for_the_synthetic_handoff(self):
        original = self.json("ui_export_manifest.json")
        for field, value in (("synthetic_labels", False), ("bundle_kind", "ordinary_ui_export")):
            self.write_json("ui_export_manifest.json", {**original, field: value})
            with self.assertRaisesRegex(ValueError, "dedicated synthetic"):
                viewer.load_bundle(self.bundle)

    def test_nonfinite_csv_score_and_duplicate_csv_ids_are_rejected(self):
        path = self.bundle / "patient_predictions.csv"
        original = path.read_text()
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fields = reader.fieldnames
        rows[0]["prob_mif"] = "nan"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, "finite"):
            viewer.load_bundle(self.bundle)
        path.write_text(original + original.splitlines()[1] + "\n")
        with self.assertRaisesRegex(ValueError, "duplicate patient"):
            viewer.load_bundle(self.bundle)

    @unittest.skipUnless(HAS_PIL, "optional Pillow/Streamlit demo dependencies are not installed")
    def test_transparency_is_composited_only_in_a_white_display_copy(self):
        from PIL import Image
        image = self.bundle / "transparent.png"
        Image.new("RGBA", (2, 2), (0, 0, 0, 0)).save(image)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        display = viewer.white_image(image)
        self.assertEqual(display.mode, "RGB")
        self.assertEqual(display.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), digest)

    @unittest.skipUnless(HAS_STREAMLIT, "install requirements-demo.txt to execute the real Streamlit AppTest")
    def test_actual_streamlit_dropdown_changes_all_five_patient_scores_plots_and_narratives(self):
        from streamlit.testing.v1 import AppTest
        from icb_copilot.experiment import run_experiment
        from icb_copilot.handoff import prepare_handoff
        from icb_copilot.handoff_export import export_handoff_bundle
        prepared = self.bundle.parent / "prepared"
        run = self.bundle.parent / "run"
        published = self.bundle.parent / "published-ui"
        prepare_handoff(SOURCE, prepared)
        run_experiment(prepared / "patients.jsonl", run, Copilot(backend="mock"))
        export_handoff_bundle(SOURCE, run, published)
        self.bundle = published
        script = (f"import sys\nsys.path.insert(0, {str(ROOT)!r})\n"
                  "from demo.handoff_app import main\n"
                  f"main(['--bundle-dir', {str(self.bundle)!r}])\n")
        at = AppTest.from_string(script, default_timeout=15).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.selectbox(key="handoff_patient").options, ["S01", "S02", "S03", "S04", "S05"])
        loaded = viewer.load_bundle(self.bundle)
        image_urls = [set(), set()]
        for pid, patient in loaded["patients"].items():
            with self.subTest(patient=pid):
                at.selectbox(key="handoff_patient").select(pid).run()
                self.assertEqual(len(at.exception), 0)
                self.assertTrue(any(item.value == f"Patient {pid}" for item in at.subheader))
                self.assertEqual([m.value for m in at.metric], [f"{patient['scores'][m]:.4f}" for m in viewer.MODALITIES])
                self.assertEqual(len(at.image), 2)
                for index, image in enumerate(at.image):
                    image_urls[index].add(tuple(image.value))
                self.assertEqual(len(at.get("download_button")), 2)
                self.assertTrue(any(item.value == patient["result"]["narrative"] for item in at.main.text))
                self.assertTrue(any(item.value == patient["narrative"] for item in at.text))
                self.assertTrue(any("Mock — no language model executed" in item.value for item in at.text))
                self.assertFalse(any("Clinical figure warning" in item.value for item in at.warning))
                self.assertFalse(any("mIF score mismatch" in item.value for item in at.warning))
                self.assertEqual(len(at.sidebar.selectbox), 0)
                if pid == "S03":
                    self.assertTrue(any("false negative" in item.value for item in at.warning))
                if pid == "S04":
                    self.assertFalse(any("false negative" in item.value for item in at.warning))
                if pid == "S05":
                    self.assertTrue(any("false positive" in item.value for item in at.warning))
        self.assertEqual([len(urls) for urls in image_urls], [5, 5])


if __name__ == "__main__":
    unittest.main()
