"""Check skill loading, patient-grounded context, and reviewable raw generations."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from icb_copilot.backends import build_messages
from icb_copilot.copilot import Copilot, screen_narrative, summarize_evidence
from icb_copilot.experiment import run_experiment
from icb_copilot.io import load_jsonl
from icb_copilot.prompts import PROMPT_SHA256, PROMPT_VERSION, SYSTEM_PROMPT, WORKED_EXAMPLES
from icb_copilot.schema import PatientPrediction

from helpers import prediction

ROOT = Path(__file__).resolve().parents[1]


class PromptTests(unittest.TestCase):
    def test_runtime_includes_packaged_skill_and_worked_examples(self):
        messages = build_messages(PatientPrediction.from_dict(prediction()).to_dict())
        self.assertEqual(messages[0]["content"], SYSTEM_PROMPT)
        for example in WORKED_EXAMPLES:
            self.assertIn(example["output"]["interpretation"], messages[0]["content"])
        self.assertEqual(len(PROMPT_SHA256), 64)

    def test_worked_examples_match_real_comparison_flags_and_pass_screen(self):
        for example in WORKED_EXAMPLES:
            with self.subTest(example=example):
                evidence = copy.deepcopy(example["input"])
                supplied = evidence.pop("comparison")
                patient = PatientPrediction.from_dict({"patient_id": "EXAMPLE", **evidence}).to_dict()
                comparison, _ = summarize_evidence(patient)
                for key, value in supplied.items():
                    self.assertEqual(comparison[key], value)
                text, issues = screen_narrative(json.dumps(example["output"]), comparison=comparison)
                self.assertEqual(text, example["output"]["interpretation"])
                self.assertEqual(issues, [])

    def test_current_patient_context_is_separate_and_labels_do_not_leak(self):
        patients = load_jsonl(ROOT / "examples/prompt_quality_cases.jsonl")
        seen = []

        def generator(conversations):
            seen.extend(conversations)
            return [json.dumps(WORKED_EXAMPLES[0]["output"])] * len(conversations)

        Copilot(backend="vllm", generator=generator).interpret_many(patients)
        for conversation, patient in zip(seen, patients):
            payload = json.loads(conversation[-1]["content"].split("\n", 1)[1])
            self.assertEqual(payload["comparison"], summarize_evidence(patient.to_dict())[0])
            self.assertEqual(payload["top_features"], patient.to_dict()["top_features"])
            self.assertNotIn("patient_id", payload)
            self.assertNotIn("ground_truth", payload)
            self.assertNotIn("evaluation_partition", payload)
            self.assertNotIn("<assistant>", conversation[-1]["content"])

    def test_irrelevant_generic_reply_falls_back_for_disagreement(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[1]
        generator = lambda conversations: [json.dumps(WORKED_EXAMPLES[0]["output"])] * len(conversations)
        result = Copilot(backend="vllm", generator=generator).interpret(patient)
        self.assertEqual(result["narrative_source"], "fallback")
        self.assertIn("missing_disagreement_context", result["quality"]["issues"])
        self.assertEqual(result["predictions"], patient.to_dict()["predictions"])

    def test_denied_disagreement_does_not_satisfy_discordant_case(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[1].to_dict()
        comparison = summarize_evidence(patient)[0]
        for claim in ("The model outputs do not disagree", "There is no disagreement", "Review these scores without a flagged disagreement"):
            with self.subTest(claim=claim):
                raw = json.dumps({"interpretation": claim + ". Review the supplied evidence and calibration uncertainty."})
                text, issues = screen_narrative(raw, comparison=comparison)
                self.assertIsNone(text)
                self.assertIn("missing_disagreement_context", issues)

    def test_generic_reply_falls_back_when_modalities_are_missing(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[2]
        generator = lambda conversations: [json.dumps(WORKED_EXAMPLES[0]["output"])] * len(conversations)
        result = Copilot(backend="vllm", generator=generator).interpret(patient)
        self.assertIn("missing_modality_context", result["quality"]["issues"])

    def test_matched_reply_is_retained_with_prompt_provenance(self):
        patient = load_jsonl(ROOT / "examples/mock_predictions.jsonl")[1]
        generator = lambda conversations: [json.dumps(WORKED_EXAMPLES[1]["output"])] * len(conversations)
        result = Copilot(backend="vllm", generator=generator).interpret(patient)
        self.assertEqual(result["narrative_source"], "vllm")
        self.assertEqual(result["provenance"]["prompt_version"], PROMPT_VERSION)
        self.assertEqual(result["provenance"]["prompt_sha256"], PROMPT_SHA256)
        self.assertEqual(result["predictions"], patient.to_dict()["predictions"])

    def test_patient_template_and_quality_cases_are_valid_synthetic_inputs(self):
        template = PatientPrediction.from_dict(json.loads((ROOT / "examples/patient_template.json").read_text()))
        self.assertEqual(template.data["evaluation_partition"], "synthetic")
        cases = load_jsonl(ROOT / "examples/prompt_quality_cases.jsonl")
        self.assertEqual(len(cases), 6)
        self.assertTrue(all(case.data["evaluation_partition"] == "synthetic" and case.data["ground_truth"] is None for case in cases))
        no_threshold = next(p for p in cases if p.patient_id == "P_NO_THRESHOLD")
        self.assertTrue(all(value is None for value in summarize_evidence(no_threshold.to_dict())[0]["predicted_classes"].values()))

    def test_raw_rejected_text_is_saved_separately_from_display_narrative(self):
        bad = json.dumps({"interpretation": "The treatment guarantees cure at 99%."})
        generator = lambda conversations: [bad] * len(conversations)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            manifest = run_experiment(ROOT / "examples/mock_predictions.jsonl", output,
                                      Copilot(backend="vllm", generator=generator))
            reviews = [json.loads(line) for line in (output / "generation_review.jsonl").read_text().splitlines()]
            results = [json.loads(line) for line in (output / "narratives.jsonl").read_text().splitlines()]
            self.assertIn("generation_review.jsonl", manifest["artifacts"])
            self.assertEqual([row["patient_id"] for row in reviews], [row["patient_id"] for row in results])
            for review, result in zip(reviews, results):
                self.assertEqual(review["raw_generation"], bad)
                self.assertEqual(review["screen_status"], "fallback")
                self.assertTrue(review["screen_issues"])
                self.assertNotIn(bad, result["narrative"])


if __name__ == "__main__":
    unittest.main()
