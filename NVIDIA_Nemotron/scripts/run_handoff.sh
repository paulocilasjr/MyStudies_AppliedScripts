#!/usr/bin/env bash
# Preserve Alyssa's source bundle; publish canonical input, experiment and UI copies.
set -euo pipefail
umask 077

COPILOT_ROOT_HINT=""
COPILOT_SCAN=("$@")
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root)
            [[ $# -ge 2 && "$2" == /* ]] || { printf 'An absolute project root is required.\n' >&2; exit 2; }
            COPILOT_ROOT_HINT="$2"; shift 2 ;;
        --) break ;;
        *) shift ;;
    esac
done
# SLURM spools the submitted script, so its $0 cannot locate the shared checkout.
if [[ -n "$COPILOT_ROOT_HINT" ]]; then
    PROJECT_ROOT="$(cd -- "$COPILOT_ROOT_HINT" && pwd -P)"
else
    PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
fi
[[ -f "$PROJECT_ROOT/run_hpc.sh" ]] || { printf 'Shared project checkout is unavailable.\n' >&2; exit 1; }
cd -- "$PROJECT_ROOT"
set -- ${COPILOT_SCAN[@]+"${COPILOT_SCAN[@]}"}
die() { printf 'Handoff runner: %s\n' "$*" >&2; exit 1; }
need_value() { [[ $# -ge 2 && -n "$2" ]] || die "Missing value for $1"; }
absolute_path() { case "$1" in /*) printf '%s\n' "$1" ;; *) printf '%s/%s\n' "$PROJECT_ROOT" "$1" ;; esac; }
COPILOT_BACKEND=mock
COPILOT_HANDOFF="examples/paulo_handoff"
COPILOT_OUTPUT=""
COPILOT_CONFIG="$PROJECT_ROOT/config/hpc.env"
COPILOT_EXPLICIT_CONFIG=0
COPILOT_MODEL_PATH=""
COPILOT_OFFLINE=0
COPILOT_DIRECT=0
COPILOT_EXTRA=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --backend) need_value "$@"; COPILOT_BACKEND="$2"; shift 2 ;;
        --handoff-dir) need_value "$@"; COPILOT_HANDOFF="$2"; shift 2 ;;
        --output-dir) need_value "$@"; COPILOT_OUTPUT="$2"; shift 2 ;;
        --config) need_value "$@"; COPILOT_CONFIG="$(absolute_path "$2")"; COPILOT_EXPLICIT_CONFIG=1; shift 2 ;;
        --model-path) need_value "$@"; COPILOT_MODEL_PATH="$(absolute_path "$2")"; shift 2 ;;
        --offline) COPILOT_OFFLINE=1; shift ;;
        --direct) COPILOT_DIRECT=1; shift ;;
        --project-root) need_value "$@"; shift 2 ;;
        --) shift; COPILOT_EXTRA=("$@"); break ;;
        -h|--help)
            cat <<'USAGE'
Usage: bash scripts/run_handoff.sh [OPTIONS] [-- GENERATION_OPTIONS]
  --backend mock|vllm   mock: local plumbing; vllm: bootstrap, SLURM, real model.
  --handoff-dir DIR     Source bundle (default examples/paulo_handoff).
  --output-dir DIR      New run root containing input/, experiment/, and ui/.
  --offline            vLLM only: require an already prepared environment/cache.
  --direct             vLLM only: use the current SLURM GPU allocation.
  --config PATH        Trusted HPC settings (default config/hpc.env).
  --model-path DIR     Local prepared snapshot matching configured model identity.
Relative paths resolve from the shared project root. Source handoff is not edited.
Mock runs need existing Python3.11+. HPC submits asynchronously after preparation;
it verifies accepted real vLLM output before exporting the UI bundle.
USAGE
            exit 0 ;;
        *) die "Unknown option: $1" ;;
    esac
done
case "$COPILOT_BACKEND" in mock|vllm) ;; *) die "backend must be mock or vllm" ;; esac
if [[ "$COPILOT_BACKEND" == mock && ( "$COPILOT_DIRECT" == 1 || -n "$COPILOT_MODEL_PATH" ) ]]; then
    die "--direct and --model-path require --backend vllm"
fi
COPILOT_HANDOFF="$(absolute_path "$COPILOT_HANDOFF")"
[[ -d "$COPILOT_HANDOFF" ]] || die "Handoff directory is unavailable: $COPILOT_HANDOFF"
[[ -n "$COPILOT_OUTPUT" ]] || COPILOT_OUTPUT="results/handoff-${COPILOT_BACKEND}-$(date -u +%Y%m%dT%H%M%SZ)-$$"
COPILOT_OUTPUT="$(absolute_path "$COPILOT_OUTPUT")"
[[ ! -e "$COPILOT_OUTPUT" ]] || die "Output root already exists; choose a new directory: $COPILOT_OUTPUT"
# Only generation settings may be forwarded. An argparse abbreviation must not
# redirect the imported input, backend, output or model away from verification.
COPILOT_INDEX=0
while (( COPILOT_INDEX < ${#COPILOT_EXTRA[@]} )); do
    case "${COPILOT_EXTRA[$COPILOT_INDEX]}" in
        --max-tokens|--max-model-len|--gpu-memory-utilization|--seed|--temperature|--disagreement-threshold|--batch-size)
            (( COPILOT_INDEX + 1 < ${#COPILOT_EXTRA[@]} )) || die "Missing generation-setting value"
            COPILOT_INDEX=$((COPILOT_INDEX + 2)) ;;
        --max-tokens=*|--max-model-len=*|--gpu-memory-utilization=*|--seed=*|--temperature=*|--disagreement-threshold=*|--batch-size=*)
            COPILOT_INDEX=$((COPILOT_INDEX + 1)) ;;
        *) die "Only full generation-setting names may follow --" ;;
    esac
done

COPILOT_HPC_OPTIONS=()
if [[ -f "$COPILOT_CONFIG" ]]; then
    # shellcheck source=/dev/null
    source "$COPILOT_CONFIG"
    COPILOT_HPC_OPTIONS+=(--config "$COPILOT_CONFIG")
elif [[ "$COPILOT_EXPLICIT_CONFIG" == 1 ]]; then
    die "Config file is unavailable: $COPILOT_CONFIG"
fi
HPC_ENV_PREFIX="$(absolute_path "${HPC_ENV_PREFIX:-.envs/nemotron-vllm}")"
HPC_MODEL_ID="${HPC_MODEL_ID:-nvidia/Nemotron-Mini-4B-Instruct}"
HPC_MODEL_REVISION="${HPC_MODEL_REVISION:-791833e92ebddb0bc2c1007f6d2b6764f886a2ae}"
[[ -z "$COPILOT_MODEL_PATH" ]] || COPILOT_HPC_OPTIONS+=(--model-path "$COPILOT_MODEL_PATH")
if [[ "$COPILOT_BACKEND" == vllm ]]; then
    if [[ "$COPILOT_DIRECT" == 1 && -z "${SLURM_JOB_ID:-}" ]]; then
        die "--direct requires an existing SLURM GPU allocation"
    fi
    if [[ "$COPILOT_DIRECT" == 0 && -z "${SLURM_JOB_ID:-}" ]]; then
        command -v sbatch >/dev/null || die "sbatch unavailable; use --backend mock locally"
    fi
    if [[ "$COPILOT_OFFLINE" == 0 ]]; then
        bash "$PROJECT_ROOT/run_hpc.sh" --prepare-only ${COPILOT_HPC_OPTIONS[@]+"${COPILOT_HPC_OPTIONS[@]}"}
    fi
    [[ -x "$HPC_ENV_PREFIX/bin/python" ]] || die "Prepared environment missing; omit --offline for approved public preparation"
    if [[ "$COPILOT_DIRECT" == 0 && -z "${SLURM_JOB_ID:-}" ]]; then
        COPILOT_LOGS="$(absolute_path "${HPC_LOG_DIR:-logs}")"
        mkdir -p -- "$COPILOT_LOGS" "$PROJECT_ROOT/.state"
        COPILOT_SBATCH=(--parsable --job-name "${HPC_JOB_NAME:-nemotron-handoff}"
            --partition "${HPC_PARTITION:-red}" --gres "${HPC_GRES:-gpu:a30:1}"
            --mem "${HPC_MEMORY:-32G}" --time "${HPC_TIME:-04:00:00}" --cpus-per-task "${HPC_CPUS:-4}"
            --chdir "$PROJECT_ROOT" --output "$COPILOT_LOGS/handoff-%j.out" --error "$COPILOT_LOGS/handoff-%j.err")
        [[ -z "${HPC_ACCOUNT:-}" ]] || COPILOT_SBATCH+=(--account "$HPC_ACCOUNT")
        [[ -z "${HPC_QOS:-}" ]] || COPILOT_SBATCH+=(--qos "$HPC_QOS")
        COPILOT_JOB_ARGS=(--project-root "$PROJECT_ROOT" --backend vllm --direct --offline
            --handoff-dir "$COPILOT_HANDOFF" --output-dir "$COPILOT_OUTPUT")
        COPILOT_JOB_ARGS+=("${COPILOT_HPC_OPTIONS[@]+"${COPILOT_HPC_OPTIONS[@]}"}")
        COPILOT_SUBMISSION="$(sbatch "${COPILOT_SBATCH[@]}" "$PROJECT_ROOT/scripts/run_handoff.sh" "${COPILOT_JOB_ARGS[@]}" -- ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"})"
        COPILOT_JOB_ID="${COPILOT_SUBMISSION%%;*}"
        [[ "$COPILOT_JOB_ID" =~ ^[0-9]+$ ]] || die "Unexpected sbatch response: $COPILOT_SUBMISSION"
        printf '%s\n' "$COPILOT_JOB_ID" > "$PROJECT_ROOT/.state/last_handoff_job_id"
        printf 'Submitted handoff job %s\nstdout: %s/handoff-%s.out\nstderr: %s/handoff-%s.err\nRun root: %s\n' \
            "$COPILOT_JOB_ID" "$COPILOT_LOGS" "$COPILOT_JOB_ID" "$COPILOT_LOGS" "$COPILOT_JOB_ID" "$COPILOT_OUTPUT"
        exit 0
    fi
    COPILOT_PYTHON="$HPC_ENV_PREFIX/bin/python"
else
    COPILOT_PYTHON="${COPILOT_PYTHON:-python3}"
    command -v "$COPILOT_PYTHON" >/dev/null || die "Python3.11+ is required"
fi
export PYTHONPATH="$PROJECT_ROOT/src" PYTHONNOUSERSITE=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1 VLLM_NO_USAGE_STATS=1 VLLM_DO_NOT_TRACK=1 DO_NOT_TRACK=1
mkdir -p -- "$(dirname -- "$COPILOT_OUTPUT")"
mkdir -- "$COPILOT_OUTPUT"
COPILOT_INPUT="$COPILOT_OUTPUT/input/patients.jsonl"
COPILOT_RUN="$COPILOT_OUTPUT/experiment"
COPILOT_UI="$COPILOT_OUTPUT/ui"
"$COPILOT_PYTHON" -m nemotron_copilot prepare-handoff --handoff-dir "$COPILOT_HANDOFF" --output-dir "$COPILOT_OUTPUT/input"
if [[ "$COPILOT_BACKEND" == vllm ]]; then
    bash "$PROJECT_ROOT/run_hpc.sh" --direct --offline \
        --input "$COPILOT_INPUT" --output-dir "$COPILOT_RUN" \
        ${COPILOT_HPC_OPTIONS[@]+"${COPILOT_HPC_OPTIONS[@]}"} -- ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"}
    "$COPILOT_PYTHON" -m nemotron_copilot verify-run --input "$COPILOT_INPUT" --output-dir "$COPILOT_RUN" \
        --require-synthetic --require-vllm --expected-model-id "$HPC_MODEL_ID" --expected-model-revision "$HPC_MODEL_REVISION"
else
    "$COPILOT_PYTHON" -m nemotron_copilot experiment --backend mock --input "$COPILOT_INPUT" --output-dir "$COPILOT_RUN" \
        ${COPILOT_EXTRA[@]+"${COPILOT_EXTRA[@]}"}
    "$COPILOT_PYTHON" -m nemotron_copilot verify-run --input "$COPILOT_INPUT" --output-dir "$COPILOT_RUN" --require-synthetic
fi
"$COPILOT_PYTHON" -m nemotron_copilot export-handoff-ui \
    --handoff-dir "$COPILOT_HANDOFF" --run-dir "$COPILOT_RUN" --output-dir "$COPILOT_UI"
printf 'Handoff workflow completed.\nRun: %s\nUI bundle: %s\n' "$COPILOT_RUN" "$COPILOT_UI"
