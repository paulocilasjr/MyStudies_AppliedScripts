"""Public artifact preparation and local hardware diagnostics; no patient input."""
from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .backends import DEFAULT_MODEL, DEFAULT_REVISION


def prepare_model(model_id: str = DEFAULT_MODEL, revision: str = DEFAULT_REVISION,
                  cache_dir: str = ".cache/huggingface/hub") -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("revision must be an exact 40-character commit hash for reproducibility")
    os.environ.update({"HF_HUB_DISABLE_TELEMETRY": "1", "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1", "DO_NOT_TRACK": "1"})
    try:
        # Optional (requirements-local.txt): trust the OS certificate store, e.g.
        # an institutional TLS-inspection root that certifi does not include.
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass
    from huggingface_hub import snapshot_download
    from huggingface_hub.utils import disable_progress_bars
    if not sys.stderr.isatty():
        disable_progress_bars()
    cache = Path(cache_dir).expanduser().resolve()
    cache.mkdir(parents=True, exist_ok=True)
    snapshot = Path(snapshot_download(repo_id=model_id, revision=revision, cache_dir=str(cache),
                                     token=False, allow_patterns=["*.json", "*.safetensors", "pytorch_model*.bin", "*.model", "*.txt",
                                                                  "tokenizer*", "*.tiktoken", "README.md", "LICENSE*",
                                                                  "nvidia-community-model-license*.pdf"])).resolve()
    config = snapshot / "config.json"
    if not config.is_file() or not (snapshot / "tokenizer_config.json").is_file():
        raise ValueError("downloaded snapshot lacks required model/tokenizer configuration")
    index = next((snapshot / name for name in ("model.safetensors.index.json", "pytorch_model.bin.index.json")
                  if (snapshot / name).is_file()), None)
    if index:
        weights = sorted(set(json.loads(index.read_text())["weight_map"].values()))
    else:
        weights = [p.name for p in snapshot.glob("*.safetensors")] or [p.name for p in snapshot.glob("pytorch_model*.bin")]
    if not weights or not all((snapshot / weight).is_file() and (snapshot / weight).stat().st_size > 0 for weight in weights):
        raise ValueError("model weight snapshot is incomplete")
    manifest = {"model_id": model_id, "revision": revision, "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
                "weight_files": [{"name": weight, "bytes": (snapshot / weight).stat().st_size} for weight in weights]}
    (snapshot / "copilot_model_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return str(snapshot)


def _check_pins(report: dict, expected: dict) -> None:
    report["packages"] = {}
    for package, pin in expected.items():
        try:
            actual = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            actual = "missing"
        report["packages"][package] = actual
        if actual != pin:
            report["errors"].append(f"{package} requires {pin}, found {actual}")


def doctor(backend: str = "mock") -> dict:
    report = {"backend": backend, "python": platform.python_version(), "os": platform.system(),
              "machine": platform.machine(), "checks": [], "errors": []}
    if sys.version_info < (3, 11):
        report["errors"].append("Python 3.11 or newer is required")
    if backend == "mock":
        report["checks"].append("mock backend needs no GPU or external packages")
    elif backend == "vllm":
        if platform.system() != "Linux" or platform.machine() != "x86_64":
            report["errors"].append("pinned GPU runtime requires Linux x86_64")
        libc, version = platform.libc_ver()
        report["glibc"] = version if libc == "glibc" else "unknown"
        if libc != "glibc" or not version or tuple(int(v) for v in version.split(".")[:2]) < (2, 28):
            report["errors"].append("pinned PyTorch wheels require glibc >=2.28")
        _check_pins(report, {"vllm": "0.10.2", "torch": "2.8.0+cu128", "transformers": "4.55.2", "huggingface-hub": "0.34.4"})
        if not report["errors"]:
            try:
                result = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                                        text=True, capture_output=True, check=True, timeout=15)
                drivers = sorted(set(result.stdout.strip().splitlines()))
                report["drivers"] = drivers
                if not drivers or any(tuple(int(x) for x in version.split(".")[:2]) < (570, 26) for version in drivers):
                    report["errors"].append("native CUDA 12.8 wheels require NVIDIA driver >=570.26 in this deployment")
                if not report["errors"]:
                    import torch
                    report["torch_cuda"] = torch.version.cuda
                    if torch.version.cuda != "12.8" or not torch.cuda.is_available():
                        report["errors"].append("CUDA 12.8 runtime and an allocated visible GPU are required")
                    else:
                        capability = torch.cuda.get_device_capability(0)
                        properties = torch.cuda.get_device_properties(0)
                        report["gpu"] = {"name": properties.name, "compute_capability": list(capability),
                                         "vram_gib": round(properties.total_memory / 1024 ** 3, 2)}
                        if capability < (7, 0) or not torch.cuda.is_bf16_supported():
                            report["errors"].append("this bfloat16 deployment requires a GPU with BF16 support (A30 is supported)")
                        if properties.total_memory < 20 * 1024 ** 3:
                            report["errors"].append("this unquantized deployment requires at least 20 GiB GPU memory")
                        if not report["errors"]:
                            torch.zeros(1, dtype=torch.bfloat16, device="cuda")
                            torch.cuda.synchronize()
                            report["checks"].append("CUDA allocation and synchronization succeeded")
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                report["errors"].append(f"GPU runtime check failed ({type(exc).__name__}); inspect allocation and driver installation")
    elif backend == "transformers":
        _check_pins(report, {"torch": "2.8.0", "transformers": "4.55.2", "huggingface-hub": "0.34.4"})
        if not report["errors"]:
            try:
                import torch
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                report["device"] = device
                torch.ones(1, dtype=torch.bfloat16, device=device).sum().item()
                report["checks"].append(f"bfloat16 allocation on {device} succeeded")
                if device == "cpu":
                    report["checks"].append("Apple MPS unavailable; CPU generation works but is much slower")
            except (OSError, RuntimeError) as exc:
                report["errors"].append(f"PyTorch device check failed ({type(exc).__name__})")
    else:
        raise ValueError("backend must be mock, vllm, or transformers")
    report["ok"] = not report["errors"]
    return report
