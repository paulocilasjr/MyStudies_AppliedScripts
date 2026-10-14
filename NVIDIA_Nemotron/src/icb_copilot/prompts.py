"""Load the packaged task skill and examples into one focused prompt per report part."""
import hashlib
from importlib.resources import files
import json
import re

PROMPT_VERSION = "icb-interpretation-2.0"
# Report parts the model writes, each in its own short conversation; the application renders the rest.
REPLY_FIELDS = ("prediction_summary", "clinical_interpretation", "conclusion")
# The case evidence each part sees. Small models stay accurate with short, focused prompts.
FIELD_INPUTS = {"prediction_summary": ("situation", "hypothesis"),
                "clinical_interpretation": ("clinical_evidence",),
                "conclusion": ("situation", "hypothesis")}

RESOURCE = files("icb_copilot").joinpath("skills/icb-interpretation")
skill = RESOURCE.joinpath("SKILL.md").read_text(encoding="utf-8")
_, separator, body = skill.partition("\n---\n")
if not skill.startswith("---\n") or not separator or not body.strip():
    raise ValueError("packaged interpretation skill is missing its frontmatter/body")
_parts = re.split(r"^## (\w+)\s*$", body.strip(), flags=re.M)
COMMON_INSTRUCTIONS, TASKS = _parts[0].strip(), {name: text.strip() for name, text in zip(_parts[1::2], _parts[2::2])}
if set(TASKS) != set(REPLY_FIELDS):
    raise ValueError("packaged interpretation skill needs one section per report part")
# Each example keeps its synthetic source evidence for tests; a part's prompt shows only its inputs and text.
WORKED_EXAMPLES = json.loads(RESOURCE.joinpath("references/prompt-examples.json").read_text(encoding="utf-8"))
FIELD_PROMPTS = {
    field: COMMON_INSTRUCTIONS + "\n\nTask: " + TASKS[field]
    + "\n\nSynthetic worked examples (not current-patient evidence):\n"
    + json.dumps([{"input": {key: example["input"][key] for key in FIELD_INPUTS[field]},
                   "output": {"text": example["output"][field]}} for example in WORKED_EXAMPLES],
                 ensure_ascii=True, separators=(",", ":"))
    for field in REPLY_FIELDS}
PROMPT_SHA256 = hashlib.sha256("\n\x00".join(FIELD_PROMPTS[field] for field in REPLY_FIELDS).encode()).hexdigest()
