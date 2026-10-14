#!/usr/bin/env python3
"""Package source and named synthetic fixtures, excluding local data and caches."""
from pathlib import Path
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ["README.md", "pyproject.toml", "requirements-vllm.txt", "run_hpc.sh", ".gitignore",
         "config/hpc.env.example", "examples/mock_predictions.jsonl",
         "examples/upstream/clinical_predictions.csv", "examples/upstream/mif_predictions.csv",
         "examples/upstream/fused_predictions.csv", "examples/upstream/clinical_context.jsonl",
         "docs/hpc.md", "docs/integration.md", "docs/demo_ui.md", "docs/research_review.md",
         "docs/first_hpc_smoke.md", "docs/patient_inputs.md", "docs/prompt_review.md",
         "examples/patient_template.json", "examples/prompt_quality_cases.jsonl", "scripts/package_hpc.py"]


def main():
    files = {ROOT / name for name in FILES}
    for folder, pattern in (("src", "*.py"), ("tests", "*.py"), ("scripts", "*.sh")):
        files.update((ROOT / folder).rglob(pattern))
    files.update((ROOT / "src/icb_copilot/skills").rglob("SKILL.md"))
    files.update((ROOT / "src/icb_copilot/skills").rglob("*.json"))
    if any(path.is_symlink() or not path.is_file() for path in files):
        raise SystemExit("Package inputs must be existing regular source files, without symlinks")
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    archive = destination / "nemotron-hpc-smoke.tar.gz"
    with tarfile.open(archive, "w:gz") as package:
        for path in sorted(files):
            package.add(path, arcname=str(Path("NVIDIA_Nemotron") / path.relative_to(ROOT)), recursive=False)
    archive.chmod(0o600)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = destination / "nemotron-hpc-smoke.tar.gz.sha256"
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    checksum.chmod(0o600)
    print(json.dumps({"archive": str(archive), "sha256": digest, "file_count": len(files),
                      "contents": "Source, tests, documentation, and named synthetic fixtures only; no model weights or environment."}, indent=2))


if __name__ == "__main__":
    main()
