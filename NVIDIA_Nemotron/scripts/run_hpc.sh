#!/usr/bin/env bash
# Public dependency/model preparation is separate from offline patient inference.
# Default: submit a SLURM GPU job which bootstraps itself and runs the experiment.
set -euo pipefail
umask 077
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd -- "$PROJECT_ROOT"

usage() {
    cat <<'USAGE'
Usage: bash run_hpc.sh [RUNNER_OPTIONS] [-- CLI_OPTIONS]
  --config PATH       Source trusted HPC settings (default config/hpc.env).
  --prepare-only      Prepare public packages/weights here; no GPU job or inputs.
  --offline           Require a prepared environment and local weights.
  --direct            Run here inside an existing SLURM GPU allocation.
  --smoke             Run bundled synthetic patients with real vLLM, then verify.
  --command COMMAND   experiment (default), serve, or doctor.
  --model-path DIR    Use an existing local model snapshot; skip model download.
  --input PATH        Experiment inputs (default synthetic example).
  --output-dir DIR    Experiment artifacts (default results/hpc-JOBID).
  --                  Forward remaining options to the Python command.
Relative paths resolve from the shared project root. First setup downloads public
packages/model weights only. Every experiment and server runs in offline mode.
Without --direct/--prepare-only, submission prints the job ID and log locations.
USAGE
}
die() { printf 'HPC runner: %s\n' "$*" >&2; exit 1; }
need_value() { [[ $# -ge 2 && -n "$2" ]] || die "Missing value for $1"; }
absolute_path() { case "$1" in /*) printf '%s\n' "$1" ;; *) printf '%s/%s\n' "$PROJECT_ROOT" "$1" ;; esac; }

# Locate the config before reading it; replay the exact original arguments when
# submitting so CLI values override config consistently on login and GPU nodes.
COPILOT_ORIGINAL=("$@")
COPILOT_CONFIG="$PROJECT_ROOT/config/hpc.env"
COPILOT_EXPLICIT_CONFIG=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config) need_value "$@"; COPILOT_CONFIG="$(absolute_path "$2")"; COPILOT_EXPLICIT_CONFIG=1; shift 2 ;;
        --) break ;;
        *) shift ;;
    esac
done
if [[ -f "$COPILOT_CONFIG" ]]; then
    # shellcheck source=/dev/null
    source "$COPILOT_CONFIG"
elif [[ "$COPILOT_EXPLICIT_CONFIG" == 1 ]]; then
    die "Config file does not exist: $COPILOT_CONFIG"
fi

HPC_CONDA_MODULE="${HPC_CONDA_MODULE:-Anaconda3/2024.02-1}"
HPC_PURGE_MODULES="${HPC_PURGE_MODULES:-1}"
HPC_ENV_PREFIX="$(absolute_path "${HPC_ENV_PREFIX:-.envs/nemotron-vllm}")"
HPC_MODEL_CACHE="$(absolute_path "${HPC_MODEL_CACHE:-.cache/huggingface/hub}")"
HPC_MODEL_ID="${HPC_MODEL_ID:-nvidia/Nemotron-Mini-4B-Instruct}"
HPC_MODEL_REVISION="${HPC_MODEL_REVISION:-791833e92ebddb0bc2c1007f6d2b6764f886a2ae}"
HPC_PARTITION="${HPC_PARTITION:-red}"
HPC_GRES="${HPC_GRES:-gpu:a30:1}"
HPC_MEMORY="${HPC_MEMORY:-32G}"
HPC_TIME="${HPC_TIME:-04:00:00}"
HPC_CPUS="${HPC_CPUS:-4}"
HPC_JOB_NAME="${HPC_JOB_NAME:-nemotron-copilot}"
HPC_LOG_DIR="$(absolute_path "${HPC_LOG_DIR:-logs}")"
HPC_ACCOUNT="${HPC_ACCOUNT:-}"
HPC_QOS="${HPC_QOS:-}"
COPILOT_PREPARE_ONLY=0
COPILOT_OFFLINE=0
COPILOT_DIRECT=0
COPILOT_SMOKE=0
COPILOT_CUSTOM_INPUT=0
COPILOT_COMMAND=experiment
COPILOT_MODEL_PATH="${HPC_MODEL_PATH:-}"
COPILOT_INPUT="examples/mock_predictions.jsonl"
COPILOT_OUTPUT=""
COPILOT_EXTRA=()
set -- ${COPILOT_ORIGINAL[@]+"${COPILOT_ORIGINAL[@]}"}
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config) need_value "$@"; shift 2 ;;
        --prepare-only) COPILOT_PREPARE_ONLY=1; shift ;;
        --offline) COPILOT_OFFLINE=1; shift ;;
        --direct) COPILOT_DIRECT=1; shift ;;
        --smoke) COPILOT_SMOKE=1; shift ;;
        --command) need_value "$@"; COPILOT_COMMAND="$2"; shift 2 ;;
        --model-path) need_value "$@"; COPILOT_MODEL_PATH="$2"; shift 2 ;;
        --input) need_value "$@"; COPILOT_INPUT="$2"; COPILOT_CUSTOM_INPUT=1; shift 2 ;;
        --output-dir) need_value "$@"; COPILOT_OUTPUT="$2"; shift 2 ;;
        --) shift; COPILOT_EXTRA=("$@"); break ;;
        -h|--help) usage; exit 0 ;;
        *) die "Unknown runner option: $1 (use -- before CLI options)" ;;
    esac
done
case "$COPILOT_COMMAND" in experiment|serve|doctor) ;; *) die "Unsupported command: $COPILOT_COMMAND" ;; esac
if [[ "$COPILOT_SMOKE" == 1 ]]; then
    [[ "$COPILOT_COMMAND" == experiment && "$COPILOT_PREPARE_ONLY" == 0 ]] || die "--smoke runs an experiment; use --prepare-only separately."
    [[ "$COPILOT_CUSTOM_INPUT" == 0 ]] || die "--smoke uses the bundled synthetic fixture; omit --input. Use a normal experiment for supplied patient records."
    # Verify exactly the experiment run we launched. Accept only complete
    # generation-setting names, including --name=value; argparse abbreviations
    # must not secretly override the synthetic input, backend or output path.
    COPILOT_SMOKE_INDEX=0
    while (( COPILOT_SMOKE_INDEX < ${#COPILOT_EXTRA[@]} )); do
        COPILOT_OPTION="${COPILOT_EXTRA[$COPILOT_SMOKE_INDEX]}"
        case "$COPILOT_OPTION" in
            --max-tokens|--max-model-len|--gpu-memory-utilization|--seed|--temperature|--disagreement-threshold|--batch-size)
                (( COPILOT_SMOKE_INDEX + 1 < ${#COPILOT_EXTRA[@]} )) || die "Missing smoke generation value for $COPILOT_OPTION"
                COPILOT_SMOKE_INDEX=$((COPILOT_SMOKE_INDEX + 2)) ;;
            --max-tokens=*|--max-model-len=*|--gpu-memory-utilization=*|--seed=*|--temperature=*|--disagreement-threshold=*|--batch-size=*)
                COPILOT_SMOKE_INDEX=$((COPILOT_SMOKE_INDEX + 1)) ;;
            *) die "--smoke does not allow forwarded $COPILOT_OPTION; use full generation-setting names or the runner's --model-path/--output-dir controls." ;;
        esac
    done
fi

if [[ "$COPILOT_PREPARE_ONLY" == 0 && "$COPILOT_DIRECT" == 0 && -z "${SLURM_JOB_ID:-}" ]]; then
    command -v sbatch >/dev/null || die "sbatch unavailable. Run on HPC; use scripts/run_local.sh for the laptop smoke test."
    mkdir -p -- "$HPC_LOG_DIR" "$PROJECT_ROOT/.state"
    COPILOT_SBATCH=(--parsable --job-name "$HPC_JOB_NAME" --partition "$HPC_PARTITION"
        --gres "$HPC_GRES" --mem "$HPC_MEMORY" --time "$HPC_TIME"
        --cpus-per-task "$HPC_CPUS" --chdir "$PROJECT_ROOT"
        --output "$HPC_LOG_DIR/slurm-%j.out" --error "$HPC_LOG_DIR/slurm-%j.err")
    [[ -z "$HPC_ACCOUNT" ]] || COPILOT_SBATCH+=(--account "$HPC_ACCOUNT")
    [[ -z "$HPC_QOS" ]] || COPILOT_SBATCH+=(--qos "$HPC_QOS")
    # sbatch reads this script via its absolute shared filesystem path; no eval
    # or --wrap interpolation of patient paths or forwarded CLI arguments.
    COPILOT_SUBMISSION="$(sbatch "${COPILOT_SBATCH[@]}" "$PROJECT_ROOT/scripts/hpc_job.sh" "$PROJECT_ROOT" ${COPILOT_ORIGINAL[@]+"${COPILOT_ORIGINAL[@]}"})"
    COPILOT_JOB_ID="${COPILOT_SUBMISSION%%;*}"
    [[ "$COPILOT_JOB_ID" =~ ^[0-9]+$ ]] || die "Unexpected sbatch response: $COPILOT_SUBMISSION"
    printf '%s\n' "$COPILOT_JOB_ID" > "$PROJECT_ROOT/.state/last_job_id"
    printf 'Submitted SLURM job %s\nstdout: %s/slurm-%s.out\nstderr: %s/slurm-%s.err\n' \
        "$COPILOT_JOB_ID" "$HPC_LOG_DIR" "$COPILOT_JOB_ID" "$HPC_LOG_DIR" "$COPILOT_JOB_ID"
    exit 0
fi
if [[ "$COPILOT_PREPARE_ONLY" == 0 && -z "${SLURM_JOB_ID:-}" ]]; then
    die "--direct requires an existing SLURM GPU allocation. Use srun --partition=red --gres=gpu:a30:1 --mem=32G --time=04:00:00 --pty bash."
fi
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || die "The pinned vLLM environment requires Linux x86_64."
command -v sha256sum >/dev/null || die "sha256sum is required for the setup fingerprint."
# PyTorch 2.8 CUDA 12.8 wheels target manylinux_2_28. Fail before a large public
# dependency download when an older host C runtime cannot load those binaries.
COPILOT_GLIBC="$(getconf GNU_LIBC_VERSION 2>/dev/null || true)"
if [[ ! "$COPILOT_GLIBC" =~ ^glibc[[:space:]]+([0-9]+)\.([0-9]+)$ ]]; then
    die "Cannot identify host glibc; the pinned wheels require glibc >=2.28."
fi
if (( BASH_REMATCH[1] < 2 || (BASH_REMATCH[1] == 2 && BASH_REMATCH[2] < 28) )); then
    die "Host $COPILOT_GLIBC is too old; pinned CUDA 12.8 wheels require glibc >=2.28. Ask the HPC team for a compatible node/container."
fi

# Load only the Python distribution module. Pip supplies its matching CUDA 12.8
# runtime and PyTorch; loading CUDA13/PyTorch modules would mix incompatible libs.
if ! type module >/dev/null 2>&1; then
    if [[ -n "${HPC_MODULE_INIT:-}" ]]; then
        [[ -f "$HPC_MODULE_INIT" ]] || die "HPC_MODULE_INIT does not exist."
        source "$HPC_MODULE_INIT"
    else
        for COPILOT_INIT in /etc/profile.d/modules.sh /usr/share/Modules/init/bash; do
            if [[ -f "$COPILOT_INIT" ]]; then source "$COPILOT_INIT"; break; fi
        done
    fi
fi
type module >/dev/null 2>&1 || die "Environment modules unavailable; set HPC_MODULE_INIT in config/hpc.env."
[[ "$HPC_PURGE_MODULES" != 1 ]] || module purge
module load "$HPC_CONDA_MODULE"
command -v conda >/dev/null || die "conda unavailable after module load $HPC_CONDA_MODULE."

export PYTHONPATH="$PROJECT_ROOT/src" PYTHONNOUSERSITE=1
unset PYTHONHOME
export HF_HOME="$PROJECT_ROOT/.cache/huggingface" HF_HUB_CACHE="$HPC_MODEL_CACHE"
export HF_HUB_DISABLE_TELEMETRY=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export VLLM_NO_USAGE_STATS=1 VLLM_DO_NOT_TRACK=1 DO_NOT_TRACK=1
export WANDB_DISABLED=true WANDB_MODE=disabled
export TOKENIZERS_PARALLELISM=false VLLM_LOGGING_LEVEL=WARNING
export PIP_DISABLE_PIP_VERSION_CHECK=1
COPILOT_STATE="$PROJECT_ROOT/.state"
mkdir -p -- "$COPILOT_STATE" "$(dirname -- "$HPC_ENV_PREFIX")" "$HPC_MODEL_CACHE"
COPILOT_FINGERPRINT="$( { cat "$PROJECT_ROOT/requirements-vllm.txt"; printf '\npython=3.11\nmodule=%s\nindex=cu128\n' "$HPC_CONDA_MODULE"; } | sha256sum | cut -d ' ' -f 1)"
COPILOT_MARKER="$HPC_ENV_PREFIX/.copilot-setup.sha256"
COPILOT_LOCK="${HPC_ENV_PREFIX}.setup-lock"
COPILOT_LOCK_OWNED=0
COPILOT_TEMP=""
cleanup() {
    [[ -z "$COPILOT_TEMP" ]] || rm -f -- "$COPILOT_TEMP"
    if [[ "$COPILOT_LOCK_OWNED" == 1 ]]; then rm -f -- "$COPILOT_LOCK/owner"; rmdir -- "$COPILOT_LOCK" || true; fi
}
trap cleanup EXIT
if ! mkdir -- "$COPILOT_LOCK" 2>/dev/null; then
    die "Setup lock exists: $COPILOT_LOCK. Wait for the active setup to finish; if stale, verify its owner is no longer running before removing the lock directory."
fi
COPILOT_LOCK_OWNED=1
printf 'host=%s pid=%s job=%s\n' "$(hostname)" "$$" "${SLURM_JOB_ID:-login}" > "$COPILOT_LOCK/owner"
COPILOT_ENV_READY=0
if [[ -x "$HPC_ENV_PREFIX/bin/python" && -f "$COPILOT_MARKER" && "$(cat "$COPILOT_MARKER")" == "$COPILOT_FINGERPRINT" ]]; then
    COPILOT_ENV_READY=1
fi
if [[ "$COPILOT_ENV_READY" == 0 ]]; then
    [[ "$COPILOT_OFFLINE" == 0 ]] || die "Offline environment missing or fingerprint changed. Run bash run_hpc.sh --prepare-only on a node with internet first."
    unset HF_HUB_OFFLINE TRANSFORMERS_OFFLINE
    if [[ ! -x "$HPC_ENV_PREFIX/bin/python" ]]; then
        conda create --yes --prefix "$HPC_ENV_PREFIX" python=3.11 pip
    fi
    "$HPC_ENV_PREFIX/bin/python" -c 'import sys; assert sys.version_info[:2] == (3, 11), "The dedicated environment must use Python 3.11"'
    "$HPC_ENV_PREFIX/bin/python" -m pip install --only-binary=:all: \
        --extra-index-url https://download.pytorch.org/whl/cu128 \
        --requirement "$PROJECT_ROOT/requirements-vllm.txt"
    "$HPC_ENV_PREFIX/bin/python" -m pip check
    "$HPC_ENV_PREFIX/bin/python" -m pip freeze > "$COPILOT_STATE/requirements-resolved.txt"
    printf '%s\n' "$COPILOT_FINGERPRINT" > "$COPILOT_MARKER"
fi
export PATH="$HPC_ENV_PREFIX/bin:$PATH"
COPILOT_PYTHON="$HPC_ENV_PREFIX/bin/python"
# Catch a manually modified environment before model download or patient input.
"$COPILOT_PYTHON" - <<'PY'
import importlib.metadata
import sys
assert sys.version_info[:2] == (3, 11), "Expected Python 3.11"
for package, expected in {"vllm": "0.10.2", "torch": "2.8.0+cu128", "transformers": "4.55.2", "huggingface-hub": "0.34.4"}.items():
    actual = importlib.metadata.version(package)
    if actual != expected:
        raise SystemExit(f"Environment changed: {package}={actual}; expected {expected}. Remove the .copilot-setup.sha256 marker and prepare again.")
PY

if [[ "$COPILOT_PREPARE_ONLY" == 0 ]]; then
    # Check the allocated GPU/driver before fetching gigabytes of model weights.
    # No patient files are read by doctor, even during online public preparation.
    "$COPILOT_PYTHON" -m nemotron_copilot doctor --backend vllm
    if [[ "$COPILOT_COMMAND" == doctor ]]; then exit 0; fi
fi

if [[ "$COPILOT_COMMAND" != doctor || "$COPILOT_PREPARE_ONLY" == 1 ]]; then
    if [[ -n "$COPILOT_MODEL_PATH" ]]; then
        COPILOT_MODEL_PATH="$(absolute_path "$COPILOT_MODEL_PATH")"
    else
        COPILOT_MODEL_KEY="$(printf '%s\n%s\n%s\n' "$HPC_MODEL_ID" "$HPC_MODEL_REVISION" "$HPC_MODEL_CACHE" | sha256sum | cut -d ' ' -f 1)"
        COPILOT_MODEL_MARKER="$COPILOT_STATE/model-$COPILOT_MODEL_KEY.path"
        if [[ -f "$COPILOT_MODEL_MARKER" ]]; then COPILOT_MODEL_PATH="$(cat "$COPILOT_MODEL_MARKER")"; fi
        if [[ -z "$COPILOT_MODEL_PATH" || ! -f "$COPILOT_MODEL_PATH/config.json" ]]; then
            [[ "$COPILOT_OFFLINE" == 0 ]] || die "Offline model snapshot unavailable. Run --prepare-only first, or specify --model-path DIR."
            unset HF_HUB_OFFLINE TRANSFORMERS_OFFLINE
            COPILOT_TEMP="$(mktemp "$COPILOT_STATE/model-download.XXXXXX")"
            "$COPILOT_PYTHON" -m nemotron_copilot prepare-model \
                --model-id "$HPC_MODEL_ID" --revision "$HPC_MODEL_REVISION" \
                --cache-dir "$HPC_MODEL_CACHE" > "$COPILOT_TEMP"
            COPILOT_MODEL_PATH="$(cat "$COPILOT_TEMP")"
            [[ -d "$COPILOT_MODEL_PATH" && -f "$COPILOT_MODEL_PATH/config.json" ]] || die "prepare-model did not return a valid local snapshot path."
            mv -- "$COPILOT_TEMP" "$COPILOT_MODEL_MARKER"
            COPILOT_TEMP=""
        fi
    fi
    [[ -d "$COPILOT_MODEL_PATH" && -f "$COPILOT_MODEL_PATH/config.json" ]] || die "Model snapshot missing config.json: $COPILOT_MODEL_PATH"
fi
rm -f -- "$COPILOT_LOCK/owner"
rmdir -- "$COPILOT_LOCK"
COPILOT_LOCK_OWNED=0

# No network model access from this point onward. This is also required by the
# Python backend, which accepts only a local directory and disables telemetry.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
if [[ "$COPILOT_PREPARE_ONLY" == 1 ]]; then
    printf 'Preparation complete.\nEnvironment: %s\nModel snapshot: %s\nNext: bash run_hpc.sh --offline\n' "$HPC_ENV_PREFIX" "$COPILOT_MODEL_PATH"
    exit 0
fi
COPILOT_ARGS=(--backend vllm --model-path "$COPILOT_MODEL_PATH")
if [[ "$COPILOT_COMMAND" == experiment ]]; then
    if [[ -z "$COPILOT_OUTPUT" ]]; then
        if [[ "$COPILOT_SMOKE" == 1 ]]; then
            COPILOT_OUTPUT="results/gpu-smoke-${SLURM_JOB_ID}"
        else
            COPILOT_OUTPUT="results/hpc-${SLURM_JOB_ID}"
        fi
    fi
    COPILOT_ARGS+=(--input "$COPILOT_INPUT" --output-dir "$COPILOT_OUTPUT")
fi
if [[ "$COPILOT_SMOKE" == 1 ]]; then
    printf 'GPU smoke: real vLLM generation using bundled synthetic patient records.\n'
    "$COPILOT_PYTHON" -m nemotron_copilot experiment "${COPILOT_ARGS[@]}" ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"}
    # Artifacts from a completed experiment remain available for diagnosis if
    # all generated prose falls back or any acceptance invariant fails.
    "$COPILOT_PYTHON" -m nemotron_copilot verify-run \
        --input "$COPILOT_INPUT" --output-dir "$COPILOT_OUTPUT" \
        --require-vllm --require-synthetic \
        --expected-model-id "$HPC_MODEL_ID" \
        --expected-model-revision "$HPC_MODEL_REVISION"
    printf 'GPU smoke verification passed. Results: %s\n' "$(absolute_path "$COPILOT_OUTPUT")"
    exit 0
fi
exec "$COPILOT_PYTHON" -m nemotron_copilot "$COPILOT_COMMAND" "${COPILOT_ARGS[@]}" ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"}
