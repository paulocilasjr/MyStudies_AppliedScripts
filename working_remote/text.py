(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ sacct -X -j 22457467,22457724,22457725,22457726 \
>   -o JobID,JobName%36,State%24,ExitCode,Elapsed
TEST_LOG_DIR/$PUBLIC_RUN_TAG/build_public.22457724.log"

"$RX_PYTHON_TEST" - "$TEST_DOWNLOAD_DIR/cohort_access_manifest.json" <<'PY'
import json
import sys
from pathlib import JobID                                     JobName                    State ExitCode    Elapsed
------------ ------------------------------------ ------------------------ -------- ----------
Path

manifest =22457467                           rx_E09_analyze                COMPLETED      0:0   00:21:29
22457724                              public_itrp                   FAILED      1:0   00:00:36
22457725                           prepare_public                  PENDING      0:0   00:00:00
22457726                            submit_public                  PENDING      0:0   00:00:00
 json.loads(Path(sys.argv[1]).read_text())
for cohort in manifest["cohorts"]:
    for artifact in cohort.get("public_artifacts", []):
        if artifact.get("status") != "downloaded":
            print(cohort["cohort"], artifact["name"], artifact.get("error", artifact["status"]))
PY(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ tail -n 60 "$TEST_LOG_DIR/$PUBLIC_RUN_TAG/build_public.22457724.log"
/home/4475918/.conda/envs/compass-foundation-test/lib/python3.10/site-packages/openpyxl/worksheet/_reader.py:329: UserWarning: Unknown extension is not supported and will be removed
  warn(msg)
Traceback (most recent call last):
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_test/scripts/04_build_public_itrp.py", line 560, in <module>
    main()
  File "/share/lab_goecks/paulo/federated-learning-model/compass_hpc_foundation_model_test/scripts/04_build_public_itrp.py", line 508, in main
    raise RuntimeError(f"Need {args.minimum_cohorts} complete cohorts for LOCO; found {complete}")
RuntimeError: Need 16 complete cohorts for LOCO; found ['Choueiri', 'Gide', 'Hugo', 'IMVigor210', 'IMmotion150', 'Kim', 'Liu', 'Miao', 'Riaz', 'Rose', 'Snyder', 'Zhao']
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "$RX_PYTHON_TEST" - "$TEST_DOWNLOAD_DIR/cohort_access_manifest.json" <<'PY'
> import json
> import sys
> from pathlib import Path
>
> manifest = json.loads(Path(sys.argv[1]).read_text())
> for cohort in manifest["cohorts"]:
>     for artifact in cohort.get("public_artifacts", []):
>         if artifact.get("status") != "downloaded":
>             print(cohort["cohort"], artifact["name"], artifact.get("error", artifact["status"]))
> PY
SU2CLC1 SU2C-MARK_Source_Data.zip URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
Rose Rose_clinical.tsv URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
Riaz Riaz_clinical.tsv URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
Allen CPB_melanoma_code-master.zip URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
MGH CPB_melanoma_code-master.zip URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
Hugo Hugo_clinical.tsv URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
SU2CLC2 SU2C-MARK_Source_Data.zip URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
Snyder Snyder_clinical.tsv URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain (_ssl.c:1007)'))
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457725  red prepare_publ  4475918 PD       0:00   12:00:00   1   8       N/A  64G (DependencyNeverSatisfied)
          22457726  red submit_publi  4475918 PD       0:00      30:00   1   1       N/A   2G (Dependency)
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
