set -a; source hpc/site.env; set +a        # brings in ITERATION_ROOT, CLINICAL_RESOURCES, etc. from the core run

# Interpreter paths (jobs call these directly, with no conda activation)
conda activate compass-foundation-test; RX_PYTHON_TEST="$(command -v python)"; conda deactivate
conda activate compass-federated;        RX_PYTHON_FED="$(command -v python)";  conda deactivate

# Slurm resources: copy the example and reuse your tested partition/account/QoS
mkdir -p sources/raw/HPC_reviewer_experiments
python3 - "$CLINICAL_RESOURCES" <<'PY'
import json, sys
resources = json.load(open("HPC_reviewer_experiments/config/resources.example.json"))
resources["site"].update(json.load(open(sys.argv[1])).get("site", {}))
json.dump(resources, open("sources/raw/HPC_reviewer_experiments/resources.reviewer.json", "w"), indent=2)
print(resources["site"])
PY

# Append the reviewer variables (absolute paths are written now)
cat >> hpc/site.env <<EOF

# ---- HPC_reviewer_experiments ----
RX_ROOT=$(pwd)/sources/raw/HPC_reviewer_experiments/run_$(date -u +%Y%m%d)
RX_PYTHON_TEST=${RX_PYTHON_TEST}
RX_PYTHON_FED=${RX_PYTHON_FED}
RX_RESOURCES=$(pwd)/sources/raw/HPC_reviewer_experiments/resources.reviewer.json
CORE_ITERATION_ROOT=${ITERATION_ROOT}
NEW_MODELS=${ITERATION_ROOT}/sample_objective_launch/finalized/models.tsv
CORE_LFT_PACKAGE=${ITERATION_ROOT}/new_nested_LFT/package_manifest.json
CORE_PFT_PACKAGE=${ITERATION_ROOT}/new_nested_PFT/package_manifest.json
PUBLISHED_REFERENCE=${ITERATION_ROOT}/published_references/published_matching_eight_cohorts.tsv
CLINICAL_COST_REFERENCE=${ITERATION_ROOT}/new_nested_LFT_launch/finalized/execution_cost.tsv
GPU_HOUR_CAP=120
GTEX_METADATA=
CLINICAL_DATASET_ALL16=
IATLAS_FEATURES=
SURVIVAL_LABELS=
TCGA_SUBTYPES=
TLS_CA_CERTIFICATE=
TLS_SERVER_CERTIFICATE=
TLS_SERVER_PRIVATE_KEY=
EOF
