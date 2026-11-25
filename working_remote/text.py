sacct -X -j 22457467,22457724,22457725,22457726 \
  -o JobID,JobName%36,State%24,ExitCode,Elapsed

tail -n 60 "$TEST_LOG_DIR/$PUBLIC_RUN_TAG/build_public.22457724.log"

"$RX_PYTHON_TEST" - "$TEST_DOWNLOAD_DIR/cohort_access_manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
for cohort in manifest["cohorts"]:
    for artifact in cohort.get("public_artifacts", []):
        if artifact.get("status") != "downloaded":
            print(cohort["cohort"], artifact["name"], artifact.get("error", artifact["status"]))
PY
