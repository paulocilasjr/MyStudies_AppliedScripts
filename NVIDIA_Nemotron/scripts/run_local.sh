#!/usr/bin/env bash
# Dependency-free synthetic smoke experiment on macOS/Linux. No model download.
set -euo pipefail
umask 077
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd -- "$PROJECT_ROOT"
COPILOT_COMMAND=experiment
COPILOT_INPUT="examples/mock_predictions.jsonl"
COPILOT_OUTPUT="results/local-$(date -u +%Y%m%dT%H%M%SZ)-$$"
COPILOT_EXTRA=()
need_value() { [[ $# -ge 2 && -n "$2" ]] || { printf 'Missing value for %s\n' "$1" >&2; exit 2; }; }
while [[ $# -gt 0 ]]; do
    case "$1" in
        --command) need_value "$@"; COPILOT_COMMAND="$2"; shift 2 ;;
        --input) need_value "$@"; COPILOT_INPUT="$2"; shift 2 ;;
        --output-dir) need_value "$@"; COPILOT_OUTPUT="$2"; shift 2 ;;
        --) shift; COPILOT_EXTRA=("$@"); break ;;
        -h|--help)
            printf '%s\n' 'Usage: bash scripts/run_local.sh [--input PATH] [--output-dir DIR]' \
                '       [--command experiment|serve|doctor] [-- CLI_OPTIONS]' \
                'Relative paths resolve from the project root. Default backend: mock.'
            exit 0 ;;
        *) printf 'Unknown runner option: %s (use -- before CLI options)\n' "$1" >&2; exit 2 ;;
    esac
done
case "$COPILOT_COMMAND" in experiment|serve|doctor) ;; *) printf 'Unsupported command: %s\n' "$COPILOT_COMMAND" >&2; exit 2 ;; esac
COPILOT_PYTHON="${COPILOT_PYTHON:-python3}"
command -v "$COPILOT_PYTHON" >/dev/null || { printf 'Python 3.11+ is required.\n' >&2; exit 1; }
export PYTHONPATH="$PROJECT_ROOT/src"
export PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1 VLLM_NO_USAGE_STATS=1 DO_NOT_TRACK=1
COPILOT_ARGS=(--backend mock)
if [[ "$COPILOT_COMMAND" == experiment ]]; then
    COPILOT_ARGS+=(--input "$COPILOT_INPUT" --output-dir "$COPILOT_OUTPUT")
fi
exec "$COPILOT_PYTHON" -m nemotron_copilot "$COPILOT_COMMAND" "${COPILOT_ARGS[@]}" ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"}
