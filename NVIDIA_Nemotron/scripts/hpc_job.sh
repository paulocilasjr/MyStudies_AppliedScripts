#!/usr/bin/env bash
# sbatch copies its script into the spool, so do not resolve the project from $0.
# The login-side launcher passes its verified absolute shared filesystem path.
set -euo pipefail
[[ $# -gt 0 && "$1" == /* && -d "$1" ]] || { printf 'Missing shared project path.\n' >&2; exit 1; }
COPILOT_PROJECT_ROOT="$1"
shift
cd -- "$COPILOT_PROJECT_ROOT"
exec bash "$COPILOT_PROJECT_ROOT/scripts/run_hpc.sh" --direct "$@"
