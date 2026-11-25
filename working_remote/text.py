(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ (
>   set -e
>   ca_bundle=
>   for candidate in /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
>                    /etc/pki/tls/certs/ca-bundle.crt \
>                    /etc/ssl/certs/ca-certificates.crt; do
>     if [[ -r "$candidate" && -s "$candidate" ]]; then
>       ca_bundle="$candidate"
>       break
>     fi
>   done
>   if [[ -z "$ca_bundle" ]]; then
>     echo "A readable site CA bundle is required." >&2
>     exit 1
>   fi
>   export SSL_CERT_FILE="$ca_bundle" REQUESTS_CA_BUNDLE="$ca_bundle" CURL_CA_BUNDLE="$ca_bundle"
>   export COMPASS_RSCRIPT="$HOME/.conda/envs/compass-e13-r/bin/Rscript"
>   "$COMPASS_RSCRIPT" --version
>
>   "$RX_PYTHON_TEST" - <<'PY'
> from urllib.request import Request, urlopen
>
> urls = (
>     "https://zenodo.org/api/records/5528497/files/CPB_melanoma_code-master.zip/content",
>     "https://zenodo.org/api/records/7625517/files/Source%20Data.zip/content",
> )
> for url in urls:
>     request = Request(url, headers={"User-Agent": "compass-hpc-foundation-model-test/1.0"})
>     with urlopen(request, timeout=30) as response:
>         response.read(1)
>     print("Reachable:", url)
> PY
>
>   TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
>     bash "$TEST_CODE_DIR/scripts/submit_public_pipeline.sh"
>   scancel 22457725 22457726
> )
Rscript (R) version 4.6.2 (2026-10-29)
Reachable: https://zenodo.org/api/records/5528497/files/CPB_melanoma_code-master.zip/content
Reachable: https://zenodo.org/api/records/7625517/files/Source%20Data.zip/content
Public continuous pipeline: 22458294
Run tag:                   public_all16_e13_20261125_020600Z
Download raw FASTQ:        0
Logs:                      /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/logs/public_all16_e13_20261125_020600Z
Final prepared dataset:    /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/data/processed/public_ITRP/public_all16_e13_20261125_020600Z
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
^C
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22458294  red  public_flow  4475918  R       0:07 6-23:59:53   1   4       N/A   8G hpctpa3pc0035
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
