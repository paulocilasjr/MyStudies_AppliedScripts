"""Refresh and validate the skill's worked examples after editing them or the literature knowledge base.

Run from the project root:

    PYTHONPATH=src python3 scripts/build_prompt_examples.py

Each example's `source_evidence` (synthetic scores and features) and `output` (the three report
parts) are the editable source. This rebuilds the derived `input` the model sees, checks every
output against the report screen, and rewrites references/prompt-examples.json only if all pass.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from icb_copilot.copilot import screen_report, summarize_evidence  # noqa: E402
from icb_copilot.prompts import FIELD_INPUTS, REPLY_FIELDS  # noqa: E402
from icb_copilot.report import model_payload  # noqa: E402
from icb_copilot.schema import PatientPrediction  # noqa: E402

EXAMPLES = ROOT / "src/icb_copilot/skills/icb-interpretation/references/prompt-examples.json"


def main() -> int:
    examples = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    keys = list(dict.fromkeys(key for field in REPLY_FIELDS for key in FIELD_INPUTS[field]))
    failures = []
    for index, example in enumerate(examples):
        patient = PatientPrediction.from_dict({"patient_id": "EXAMPLE", **example["source_evidence"]}).to_dict()
        comparison, _ = summarize_evidence(patient)
        payload = model_payload(patient, comparison)
        example["input"] = {key: payload[key] for key in keys}
        replies = {field: json.dumps({"text": example["output"][field]}) for field in REPLY_FIELDS}
        sections, issues = screen_report(replies, patient=patient, comparison=comparison)
        if sections != example["output"]:
            failures.append((index, example["input"]["hypothesis"], issues))
        print(f"example {index}: {example['input']['hypothesis']} -> {'ok' if sections == example['output'] else issues}")
    if failures:
        print(f"{len(failures)} example(s) fail the screen; file not rewritten.", file=sys.stderr)
        return 1
    EXAMPLES.write_text(json.dumps(examples, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
