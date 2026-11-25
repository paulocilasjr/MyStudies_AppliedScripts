https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "${rx_cmd[@]}" submit E09 && qstat
CAL_DATASET_ALL16:-}" && -s "$CLINICAL_DATASET_ALL16/manifest.json" ]]; then
  echo "Configured all16 manifest found"
else
  echo "Configured all16 manifest missing"
fi

if [[ -n "$survival_input" && -s "$survival_input" ]]; then
  echo "Configured survival file found"
else
  echo "Configured survival file missing"
fi

if [[ -n "${TEST_PROJECT_ROOT:-}" ]]; then
  arrays="$TEST_PROJECT_ROOT/data/processed/public_ITRP"
  if [[ -d "$arrays" ]]; then
    find "$arrays" -maxdepth 2 -type f -path '*/public_all16*/manifest.json' -print
  fi
  features="${TEST_DOWNLOAD_DIR:-$TEST_PROJECT_ROOT/downloads}/iatlas_ici/iatlas-ici-features.tsv"
  if [[ -s "$features" ]]; then
    printf '%s\n' "$features"
  fi
fi/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E09/submission_20261125T015919+0000.json

             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ survival_input="${SURVIVAL_LABELS:-${IATLAS_FEATURES:-}}"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -n "${CLINICAL_DATASET_ALL16:-}" && -s "$CLINICAL_DATASET_ALL16/manifest.json" ]]; then
>   echo "Configured all16 manifest found"
> else
>   echo "Configured all16 manifest missing"
> fi
Configured all16 manifest missing
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -n "$survival_input" && -s "$survival_input" ]]; then
>   echo "Configured survival file found"
> else
>   echo "Configured survival file missing"
> fi
Configured survival file missing
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -n "${TEST_PROJECT_ROOT:-}" ]]; then
>   arrays="$TEST_PROJECT_ROOT/data/processed/public_ITRP"
>   if [[ -d "$arrays" ]]; then
>     find "$arrays" -maxdepth 2 -type f -path '*/public_all16*/manifest.json' -print
>   fi
>   features="${TEST_DOWNLOAD_DIR:-$TEST_PROJECT_ROOT/downloads}/iatlas_ici/iatlas-ici-features.tsv"
>   if [[ -s "$features" ]]; then
>     printf '%s\n' "$features"
>   fi
> fi
/share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/downloads/iatlas_ici/iatlas-ici-features.tsv
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457467  red rx_E09_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
22457466_[0-137%8]  red rx_E09_probe  4475918 PD       0:00    8:00:00   1   8 gres/gpu:  64G (Priority)
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
