"""Evaluate the packaged interpretation prompt with local Nemotron on every synthetic case set.

Run from the project root after `bash run_local_mvp.sh` has prepared the environment and model:

    PYTHONPATH=src .envs/local-mvp/bin/python scripts/evaluate_prompt.py [--output results/prompt-eval.json]

Prints the screen acceptance and every raw reply for manual review. Acceptance means the
heuristic screen passed; read each reply against its comparison before trusting a prompt.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})

from icb_copilot.backends import DEFAULT_REVISION, build_messages  # noqa: E402
from icb_copilot.copilot import Copilot  # noqa: E402
from icb_copilot.handoff import prepare_handoff  # noqa: E402
from icb_copilot.io import load_jsonl  # noqa: E402
from icb_copilot.prompts import PROMPT_SHA256, PROMPT_VERSION, REPLY_FIELDS  # noqa: E402
from icb_copilot.report import hypothesis  # noqa: E402

DEFAULT_MODEL = ROOT / ".cache/huggingface/hub/models--nvidia--Nemotron-Mini-4B-Instruct/snapshots" / DEFAULT_REVISION


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL), help="prepared local snapshot")
    parser.add_argument("--device", choices=("auto", "mps", "cpu"), default="auto")
    parser.add_argument("--output", help="optional JSON report path")
    args = parser.parse_args()
    copilot = Copilot(backend="transformers", model_path=args.model_path, device=args.device)
    report = {"prompt_version": PROMPT_VERSION, "prompt_sha256": PROMPT_SHA256, "cases": []}
    started = time.monotonic()
    with tempfile.TemporaryDirectory() as temporary:
        prepare_handoff(ROOT / "examples/paulo_handoff", Path(temporary) / "handoff")
        sets = {"handoff": Path(temporary) / "handoff/patients.jsonl",
                "mock": ROOT / "examples/mock_predictions.jsonl",
                "quality": ROOT / "examples/prompt_quality_cases.jsonl"}
        for name, path in sets.items():
            patients = load_jsonl(path)
            review = []
            results = copilot.interpret_many(patients, generation_review=review)
            tokenizer = copilot._engine._tokenizer
            for patient, result, generation in zip(patients, results, review):
                prompts = [tokenizer.apply_chat_template(build_messages(patient.to_dict(), comparison=result["comparison"], field=field),
                                                         tokenize=False, add_generation_prompt=True) for field in REPLY_FIELDS]
                report["cases"].append({"set": name, "patient_id": result["patient_id"],
                                        "hypothesis": hypothesis(result["comparison"])["statement"],
                                        "narrative_source": result["narrative_source"],
                                        "screen_issues": generation["screen_issues"],
                                        "raw_generation": generation["raw_generation"],
                                        "prompt_tokens": max(len(tokenizer(prompt)["input_ids"]) for prompt in prompts)})
    report["elapsed_seconds"] = round(time.monotonic() - started, 1)
    cases = report["cases"]
    accepted = sum(case["narrative_source"] != "fallback" for case in cases)
    print(f"{PROMPT_VERSION} ({PROMPT_SHA256[:12]}): {accepted}/{len(cases)} accepted by the screen; "
          f"largest part prompt {max(case['prompt_tokens'] for case in cases)} tokens; {report['elapsed_seconds']} s")
    for case in cases:
        print(f"\n[{case['set']}/{case['patient_id']}] {case['narrative_source']} {case['screen_issues'] or ''}")
        print(f"  hypothesis: {case['hypothesis']}")
        for field, raw in json.loads(case["raw_generation"]).items():
            try:
                print(f"  {field}: {json.loads(raw)['text']}")
            except (TypeError, ValueError, KeyError):
                print(f"  {field} (raw): {raw}")
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
