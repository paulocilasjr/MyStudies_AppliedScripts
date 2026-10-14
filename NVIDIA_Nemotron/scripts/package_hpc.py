#!/usr/bin/env python3
"""Package source and named synthetic fixtures, excluding local data and caches."""
from pathlib import Path
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ["README.md", "pyproject.toml", "requirements-vllm.txt", "requirements-demo.txt", "demo/handoff_app.py", "run_hpc.sh", ".gitignore",
         "config/hpc.env.example", "examples/mock_predictions.jsonl",
         "examples/upstream/clinical_predictions.csv", "examples/upstream/mif_predictions.csv",
         "examples/upstream/fused_predictions.csv", "examples/upstream/clinical_context.jsonl",
         "docs/hpc.md", "docs/integration.md", "docs/demo_ui.md", "docs/research_review.md",
         "docs/first_hpc_smoke.md", "docs/patient_inputs.md", "docs/prompt_review.md",
         "docs/handoff.md", "examples/patient_template.json", "examples/prompt_quality_cases.jsonl", "scripts/package_hpc.py"]

# Explicitly named synthetic handoff assets. Do not recursively package an
# arbitrary data directory: a later real-data drop must not enter this archive.
HANDOFF_FILES = ["HANDOFF_PAULO.md", "predictions/patient_predictions.csv",
                 "predictions/patient_feature_analysis.json", "predictions/feature_importances.json",
                 "predictions/narratives.json"]
HANDOFF_OPTIONAL_FILES = ["predictions/tile_predictions.csv", "predictions/tile_features.csv"]
HANDOFF_FIGURES = [f"figures/{folder}/{prefix}_S{number:02d}.{extension}"
                   for folder, prefix in (("clinical_shap", "shap_waterfall"), ("mif_features", "mif_contrast"))
                   for number in range(1, 6) for extension in ("png", "pdf")]


def main():
    files = {ROOT / name for name in FILES}
    files.update(ROOT / "examples/paulo_handoff" / name for name in HANDOFF_FILES + HANDOFF_FIGURES)
    files.update(ROOT / "examples/paulo_handoff" / name for name in HANDOFF_OPTIONAL_FILES
                 if (ROOT / "examples/paulo_handoff" / name).exists()
                 or (ROOT / "examples/paulo_handoff" / name).is_symlink())
    for folder, pattern in (("src", "*.py"), ("tests", "*.py"), ("scripts", "*.sh")):
        files.update((ROOT / folder).rglob(pattern))
    files.update((ROOT / "src/icb_copilot/skills").rglob("*.md"))
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
