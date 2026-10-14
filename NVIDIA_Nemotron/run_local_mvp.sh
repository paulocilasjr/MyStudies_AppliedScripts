#!/usr/bin/env bash
# One command for the local MVP on this computer (Apple Silicon MPS, or CPU):
# prepare the pinned Nemotron-Mini-4B-Instruct snapshot, generate narratives for
# the five synthetic handoff patients with the real model, verify and export
# them, then start the loopback copilot API and the viewer connected to it.
set -euo pipefail
umask 077
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd -- "$PROJECT_ROOT"

usage() {
    cat <<'USAGE'
Usage: bash run_local_mvp.sh [OPTIONS]
  --output-dir DIR   New run root (default results/local-mvp-<UTC timestamp>).
  --reuse-run DIR    Skip generation; serve an earlier run root's verified ui/ bundle.
  --device DEVICE    auto (default: Apple MPS when available), mps, or cpu.
  --api-port PORT    Loopback copilot API port (default 8000; next free port if busy).
  --ui-port PORT     Viewer port (default 8501; next free port if busy).
  --no-ui            Stop after generation, verification, export and summary.
  --no-browser       Start the API and viewer without opening a browser.
The first run creates .envs/local-mvp and downloads ~8.4 GB of public model
weights into .cache/huggingface/hub; later runs reuse both and work offline.
Inference runs on this computer; patient evidence is never sent to a hosted
service. Press Ctrl+C to stop the API and viewer.
USAGE
}
die() { printf '\nLocal MVP: %s\n' "$*" >&2; exit 1; }
need_value() { [[ $# -ge 2 && -n "$2" ]] || die "Missing value for $1"; }
absolute_path() { case "$1" in /*) printf '%s\n' "$1" ;; *) printf '%s/%s\n' "$PROJECT_ROOT" "$1" ;; esac; }
step() { printf '\n==> [%s/7] %s\n' "$1" "$2"; }

MVP_OUTPUT=""
MVP_REUSE=""
MVP_DEVICE=auto
MVP_API_PORT=8000
MVP_UI_PORT=8501
MVP_UI=1
MVP_BROWSER=1
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir) need_value "$@"; MVP_OUTPUT="$(absolute_path "$2")"; shift 2 ;;
        --reuse-run) need_value "$@"; MVP_REUSE="$(absolute_path "$2")"; shift 2 ;;
        --device) need_value "$@"; MVP_DEVICE="$2"; shift 2 ;;
        --api-port) need_value "$@"; MVP_API_PORT="$2"; shift 2 ;;
        --ui-port) need_value "$@"; MVP_UI_PORT="$2"; shift 2 ;;
        --no-ui) MVP_UI=0; shift ;;
        --no-browser) MVP_BROWSER=0; shift ;;
        -h|--help) usage; exit 0 ;;
        *) die "Unknown option: $1 (see --help)" ;;
    esac
done
case "$MVP_DEVICE" in auto|mps|cpu) ;; *) die "--device must be auto, mps, or cpu" ;; esac
[[ "$MVP_API_PORT" =~ ^[0-9]+$ && "$MVP_UI_PORT" =~ ^[0-9]+$ ]] || die "Ports must be numbers"
[[ -z "$MVP_OUTPUT" || -z "$MVP_REUSE" ]] || die "Use either --output-dir or --reuse-run"
if [[ -n "$MVP_REUSE" ]]; then
    MVP_RUN="$MVP_REUSE"
    [[ -f "$MVP_RUN/ui/ui_export_manifest.json" && -f "$MVP_RUN/experiment/verification.json" ]] \
        || die "Not a completed local MVP run root: $MVP_RUN"
else
    MVP_RUN="${MVP_OUTPUT:-$PROJECT_ROOT/results/local-mvp-$(date -u +%Y%m%dT%H%M%SZ)}"
    [[ ! -e "$MVP_RUN" ]] || die "Output root already exists; choose a new directory: $MVP_RUN"
fi

MVP_HANDOFF="$PROJECT_ROOT/examples/paulo_handoff"
MVP_ENV="$PROJECT_ROOT/.envs/local-mvp"
MVP_PY="$MVP_ENV/bin/python"
MVP_MODEL_ID="nvidia/Nemotron-Mini-4B-Instruct"
MVP_MODEL_REVISION="791833e92ebddb0bc2c1007f6d2b6764f886a2ae"
MVP_MODEL_CACHE="$PROJECT_ROOT/.cache/huggingface/hub"
MVP_MODEL_PATH="$MVP_MODEL_CACHE/models--nvidia--Nemotron-Mini-4B-Instruct/snapshots/$MVP_MODEL_REVISION"
export PYTHONPATH="$PROJECT_ROOT/src" PYTHONNOUSERSITE=1
copilot() { "$MVP_PY" -m nemotron_copilot "$@"; }

step 1 "Python environment (.envs/local-mvp)"
MVP_REQUIREMENTS_SHA="$(shasum -a 256 requirements-local.txt | cut -d' ' -f1)"
if [[ -x "$MVP_PY" && "$(cat "$MVP_ENV/.requirements.sha256" 2>/dev/null)" == "$MVP_REQUIREMENTS_SHA" ]]; then
    printf 'Reusing prepared environment: %s\n' "$("$MVP_PY" --version)"
else
    if [[ ! -x "$MVP_PY" ]]; then
        MVP_BASE=""
        # PyTorch 2.8 publishes wheels for Python 3.11-3.13.
        for candidate in "${MVP_BASE_PYTHON:-}" python3.12 python3.11 python3.13 python3; do
            [[ -n "$candidate" ]] && command -v "$candidate" >/dev/null || continue
            if "$candidate" -c 'import sys; raise SystemExit(not (3, 11) <= sys.version_info[:2] <= (3, 13))'; then
                MVP_BASE="$(command -v "$candidate")"; break
            fi
        done
        [[ -n "$MVP_BASE" ]] || die "Python 3.11-3.13 is required (for example: brew install python@3.12)"
        "$MVP_BASE" -m venv "$MVP_ENV"
    fi
    printf 'Installing requirements-local.txt (first run only; PyTorch, Transformers, Streamlit) ...\n'
    "$MVP_PY" -m pip install --disable-pip-version-check --quiet --upgrade pip
    "$MVP_PY" -m pip install --disable-pip-version-check --quiet -r requirements-local.txt
    printf '%s\n' "$MVP_REQUIREMENTS_SHA" > "$MVP_ENV/.requirements.sha256"
fi

step 2 "Nemotron-Mini-4B-Instruct @ ${MVP_MODEL_REVISION:0:7}"
if [[ -f "$MVP_MODEL_PATH/copilot_model_manifest.json" ]]; then
    printf 'Reusing prepared model: %s\n' "$MVP_MODEL_PATH"
else
    printf 'Downloading public weights (~8.4 GB, first run only) ...\n'
    MVP_MODEL_PATH="$(copilot prepare-model --model-id "$MVP_MODEL_ID" --revision "$MVP_MODEL_REVISION" \
        --cache-dir "$MVP_MODEL_CACHE" | tail -n 1)"
    printf 'Prepared model: %s\n' "$MVP_MODEL_PATH"
fi
# Everything after preparation is offline.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export DO_NOT_TRACK=1 TOKENIZERS_PARALLELISM=false

step 3 "Hardware check"
MVP_DOCTOR="$(copilot doctor --backend transformers)" || { printf '%s\n' "$MVP_DOCTOR" >&2; die "Local runtime check failed"; }
"$MVP_PY" - "$MVP_DOCTOR" <<'PY'
import json, sys
report = json.loads(sys.argv[1])
print(f"{report['machine']} {report['os']}, Python {report['python']}, device {report['device']}: " + "; ".join(report["checks"]))
PY

if [[ -z "$MVP_REUSE" ]]; then
    mkdir -p -- "$MVP_RUN/logs"
    printf '%s\n' "$MVP_DOCTOR" > "$MVP_RUN/logs/doctor.json"

    step 4 "Generate narratives for the five synthetic patients with local Nemotron"
    copilot prepare-handoff --handoff-dir "$MVP_HANDOFF" --output-dir "$MVP_RUN/input" > "$MVP_RUN/logs/prepare_handoff.json"
    printf 'Imported %s\n' "$MVP_RUN/input/patients.jsonl"
    copilot experiment --backend transformers --model-path "$MVP_MODEL_PATH" --device "$MVP_DEVICE" \
        --input "$MVP_RUN/input/patients.jsonl" --output-dir "$MVP_RUN/experiment" 2> >(tee "$MVP_RUN/logs/generation.log" >&2)

    step 5 "Verify the completed run"
    MVP_VERIFIED=0
    copilot verify-run --input "$MVP_RUN/input/patients.jsonl" --output-dir "$MVP_RUN/experiment" --require-synthetic \
        --require-backend transformers --expected-model-id "$MVP_MODEL_ID" --expected-model-revision "$MVP_MODEL_REVISION" \
        > /dev/null && MVP_VERIFIED=1
    # A screened-out generation is shown as a labeled deterministic fallback; any other failure stops here.
    "$MVP_PY" - "$MVP_RUN/experiment/verification.json" "$MVP_VERIFIED" <<'PY' || die "Verification failed; see $MVP_RUN/experiment/verification.json"
import json, sys
report = json.load(open(sys.argv[1]))
if sys.argv[2] == "1":
    print(f"PASS: all {report['patient_count']} narratives are accepted local Nemotron generations; evidence and scores unchanged.")
elif report["errors"] == ["all_generated_narratives_accepted"]:
    print(f"PASS with fallbacks: sources {report['source_counts']}. Screened-out generations are shown as labeled deterministic fallbacks.")
else:
    print("FAILED checks: " + ", ".join(report["errors"]), file=sys.stderr)
    raise SystemExit(1)
PY

    step 6 "Export the viewer bundle (scores, narratives, figures, audit)"
    copilot export-handoff-ui --handoff-dir "$MVP_HANDOFF" --run-dir "$MVP_RUN/experiment" \
        --output-dir "$MVP_RUN/ui" > "$MVP_RUN/logs/export_ui.json"
    printf 'UI bundle: %s\n' "$MVP_RUN/ui"
else
    printf '\n==> [4-6/7] Reusing generated, verified and exported run: %s\n' "$MVP_RUN"
    mkdir -p -- "$MVP_RUN/logs"
fi

free_port() {
    "$MVP_PY" - "$1" <<'PY'
import socket, sys
for port in range(int(sys.argv[1]), int(sys.argv[1]) + 50):
    with socket.socket() as probe:
        # Match the servers' SO_REUSEADDR so a recently closed port is not reported as busy.
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            continue
    print(port)
    break
else:
    raise SystemExit("no free loopback port found")
PY
}

summary() {
    "$MVP_PY" - "$MVP_RUN" "${1:-}" <<'PY'
import json, sys
from pathlib import Path
run, live_path = Path(sys.argv[1]), sys.argv[2]
manifest = json.loads((run / "experiment/manifest.json").read_text())
verification = json.loads((run / "experiment/verification.json").read_text())
labels = {p["patient_id"]: p["ground_truth"] for p in map(json.loads, (run / "input/patients.jsonl").read_text().splitlines())}
backend = manifest["backend"]
lines = ["# Local Nemotron MVP run", "",
         f"- Model: {backend['model']['model_id']} @ {backend['model']['revision'][:7]} via Hugging Face Transformers on {backend['execution']['device']}",
         f"- Generated {manifest['patient_count']} synthetic patient reports in {manifest['elapsed_seconds']:.1f} s (including model load); "
         f"narrative sources: {manifest['source_counts']}"]
fallbacks = manifest["source_counts"].get("fallback", 0)
if verification["ok"]:
    lines.append("- Verification: PASS; every report's prose is an accepted local Nemotron generation")
elif verification["errors"] == ["all_generated_narratives_accepted"]:
    lines.append(f"- Verification: PASS with {fallbacks} screened-out generation(s) shown as labeled deterministic report text "
                 "(see experiment/generation_review.jsonl)")
else:
    lines.append(f"- Verification: FAILED {verification['errors']} (see experiment/verification.json)")
if live_path and Path(live_path).is_file():
    live = json.loads(Path(live_path).read_text())
    lines.append(f"- Live API check: {live['patient_id']} regenerated through the loopback API in {live['seconds']:.1f} s "
                 f"(source {live['narrative_source']}; identical to batch output: {live['identical_to_batch']})")
lines += ["", "Research output on synthetic data; every report requires independent human review.", "", "## Patient reports", ""]
for result in map(json.loads, (run / "experiment/narratives.jsonl").read_text().splitlines()):
    issues = f"; issues {', '.join(result['quality']['issues'])}" if result["quality"]["issues"] else ""
    lines += [f"### {result['patient_id']} (synthetic label {labels.get(result['patient_id'])}; "
              f"prose source {result['narrative_source']}, quality {result['quality']['status']}{issues})", "",
              "```text", result["narrative"], "```", ""]
lines += ["## Output files", "",
          "| Path | Contents |", "| --- | --- |",
          "| input/patients.jsonl | Canonical records imported from examples/paulo_handoff |",
          "| experiment/narratives.jsonl | Structured result per patient: report, scores, limitations, provenance |",
          "| experiment/generation_review.jsonl | Raw model replies and screen results |",
          "| experiment/report.md, narratives.csv | Human-readable report and table |",
          "| experiment/manifest.json, verification.json | Run provenance and acceptance checks |",
          "| ui/ | Viewer bundle: scores CSV, reports JSON, figures, audit |",
          "| live_api_check.json | One live regeneration through the loopback API |",
          "| logs/ | Doctor, generation, export, API and viewer logs |"]
(run / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(line for line in lines[:lines.index("## Output files")] if line not in ("```text", "```")).rstrip())
print(f"\nFull summary: {run / 'SUMMARY.md'}")
PY
}

if [[ "$MVP_UI" == 0 ]]; then
    printf '\n==> [7/7] Summary (--no-ui: API and viewer not started)\n\n'
    summary
    exit 0
fi

step 7 "Start the local copilot API and the connected viewer"
MVP_PIDS=()
cleanup() { [[ ${#MVP_PIDS[@]} -eq 0 ]] || kill "${MVP_PIDS[@]}" 2>/dev/null || true; }
trap cleanup EXIT
trap 'exit 130' INT TERM
MVP_API_PORT="$(free_port "$MVP_API_PORT")"
MVP_API="http://127.0.0.1:$MVP_API_PORT"
# Start Python directly (not the copilot function) so $! is the server itself and cleanup reaches it.
"$MVP_PY" -m nemotron_copilot serve --backend transformers --model-path "$MVP_MODEL_PATH" --device "$MVP_DEVICE" \
    --host 127.0.0.1 --port "$MVP_API_PORT" > "$MVP_RUN/logs/api.log" 2>&1 &
MVP_PIDS+=("$!")
for _ in $(seq 1 60); do
    curl -fsS --noproxy '*' "$MVP_API/health" > /dev/null 2>&1 && break
    kill -0 "${MVP_PIDS[0]}" 2>/dev/null || die "Copilot API exited; see $MVP_RUN/logs/api.log"
    sleep 1
done
curl -fsS --noproxy '*' "$MVP_API/health" > /dev/null || die "Copilot API did not start; see $MVP_RUN/logs/api.log"
printf 'Copilot API: %s (loading the model and regenerating one patient live ...)\n' "$MVP_API"
# Exercise exactly the viewer's live-generation path once; this also loads the model.
"$MVP_PY" - "$MVP_API" "$MVP_RUN" <<'PY' || die "Live API generation failed; see $MVP_RUN/logs/api.log"
import json, sys, time
from pathlib import Path
sys.path.insert(0, "demo")
from handoff_app import live_interpret
api, run = sys.argv[1], Path(sys.argv[2])
batch = json.loads((run / "experiment/narratives.jsonl").read_text().splitlines()[0])
started = time.monotonic()
live = live_interpret(api, batch)
check = {"patient_id": live["patient_id"], "seconds": round(time.monotonic() - started, 1),
         "narrative_source": live["narrative_source"], "identical_to_batch": live["narrative"] == batch["narrative"],
         "result": live}
(run / "live_api_check.json").write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
print(f"Live check: {check['patient_id']} -> {check['narrative_source']} in {check['seconds']} s")
PY
summary "$MVP_RUN/live_api_check.json"

MVP_UI_PORT="$(free_port "$MVP_UI_PORT")"
MVP_UI_URL="http://127.0.0.1:$MVP_UI_PORT"
"$MVP_PY" -m streamlit run demo/handoff_app.py --server.address 127.0.0.1 --server.port "$MVP_UI_PORT" \
    --server.headless true --browser.gatherUsageStats false \
    -- --bundle-dir "$MVP_RUN/ui" --api-url "$MVP_API" > "$MVP_RUN/logs/ui.log" 2>&1 &
MVP_PIDS+=("$!")
for _ in $(seq 1 60); do
    curl -fsS --noproxy '*' "$MVP_UI_URL/_stcore/health" > /dev/null 2>&1 && break
    kill -0 "${MVP_PIDS[1]}" 2>/dev/null || die "Viewer exited; see $MVP_RUN/logs/ui.log"
    sleep 1
done
if [[ "$MVP_BROWSER" == 1 ]]; then
    { command -v open > /dev/null && open "$MVP_UI_URL"; } || { command -v xdg-open > /dev/null && xdg-open "$MVP_UI_URL"; } || true
fi
printf '\n================================================================\n'
printf ' Local Nemotron MVP is running\n'
printf '   Viewer:      %s\n' "$MVP_UI_URL"
printf '   Copilot API: %s  (GET /health, POST /v1/interpret)\n' "$MVP_API"
printf '   Outputs:     %s\n' "$MVP_RUN"
printf '   Logs:        %s/logs\n' "$MVP_RUN"
printf ' Press Ctrl+C to stop. Reopen later without regenerating:\n'
printf '   bash run_local_mvp.sh --reuse-run %s\n' "${MVP_RUN#"$PROJECT_ROOT"/}"
printf '================================================================\n'
wait "${MVP_PIDS[1]}"
