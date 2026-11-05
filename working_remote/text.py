python3 - /share/lab_goecks/paulo/federated-learning-model <<'PY'
import json, sys, pathlib, subprocess
root = pathlib.Path(sys.argv[1])

def find(name):
    out = subprocess.run(["find", str(root), "-name", name, "-not", "-path", "*/.git/*"],
                         capture_output=True, text=True).stdout.split()
    return [pathlib.Path(p) for p in out]

def load(p):
    try:
        return json.loads(pathlib.Path(p).read_text())
    except Exception:
        return None

print("== 1. Dataset actually used by the core foundations (preflight receipt -> package -> dataset)")
for r in find("preflight_receipt.json"):
    pkg = (load(r) or {}).get("package_manifest_path")
    if not pkg:
        continue
    ds = ((load(pkg) or {}).get("inputs") or {}).get("dataset:manifest.json", {}).get("path")
    m = load(ds) if ds else None
    print(f"{r}\n   dataset manifest: {ds}\n   counts: {(m or {}).get('counts')}")

print("\n== 2. Every unified TCGA+GTEx manifest found")
for f in find("manifest.json"):
    m = load(f)
    if isinstance(m, dict) and "GTEx" in (m.get("counts") or {}):
        print(f, m["counts"], "dataset_id:", m.get("dataset_id"))

print("\n== 3. Builder manifests (TCGA patients vs paper; GTEx retained samples)")
for name in ("tcga_dataset_manifest.json", "tcga_stage_count_deviation_from_compass.json", "gtex_dataset_manifest.json"):
    for f in find(name):
        m = load(f) or {}
        keys = ("sample_count", "exact_compass_stage_count_match", "source_samples",
                "retained_samples", "exclude_cell_derived")
        print(f, {k: m[k] for k in keys if k in m} or m)
PY
