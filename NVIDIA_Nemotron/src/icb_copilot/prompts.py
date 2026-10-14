"""Load the packaged task skill and examples into the model's actual prompt."""
import hashlib
from importlib.resources import files
import json

PROMPT_VERSION = "icb-interpretation-1.1"
RESOURCE = files("icb_copilot").joinpath("skills/icb-interpretation")
skill = RESOURCE.joinpath("SKILL.md").read_text(encoding="utf-8")
_, separator, body = skill.partition("\n---\n")
if not skill.startswith("---\n") or not separator or not body.strip():
    raise ValueError("packaged interpretation skill is missing its frontmatter/body")
WORKED_EXAMPLES = json.loads(RESOURCE.joinpath("references/prompt-examples.json").read_text(encoding="utf-8"))
SYSTEM_PROMPT = body.strip() + "\n\nSynthetic worked examples (not current-patient evidence):\n" + json.dumps(WORKED_EXAMPLES, ensure_ascii=True, separators=(",", ":"))
PROMPT_SHA256 = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()
