https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export IATLAS_FEATURES="$PWD/compass_foundation_model_test/downloads/iatlas_ici/iatlas-ici-features.tsv"
URVIVAL_LABELS
export TEST_CODE_DIR="$PWD/compass_hpc_foundation_model_test"
export PUBLIC_RUN_TAG="public_all16_e13_$(date -u +%Y%m%d_%H%M%SZ)"
export CLINICAL_DATASET_ALL16="$TEST_PROJECT_ROOT/data/processed/public_ITRP/$PUBLIC_RUN_TAG"

PUBLIC_COHORT_SET=all16 TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
  bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ unset SURVIVAL_LABELS
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export TEST_CODE_DIR="$PWD/compass_hpc_foundation_model_test"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export PUBLIC_RUN_TAG="public_all16_e13_$(date -u +%Y%m%d_%H%M%SZ)"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export CLINICAL_DATASET_ALL16="$TEST_PROJECT_ROOT/data/processed/public_ITRP/$PUBLIC_RUN_TAG"
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ PUBLIC_COHORT_SET=all16 TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
>   bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
ERROR: required COMPASS input is missing: /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/third_party/COMPASS/.git
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
22457466_[48-137%8  red rx_E09_probe  4475918 PD       0:00    8:00:00   1   8 gres/gpu:  64G (Priority)
          22457467  red rx_E09_analy  4475918 PD       0:00 2-00:00:00   1  16       N/A 128G (Dependency)
       22457466_44  red rx_E09_probe  4475918  R       0:17    7:59:43   1   8 gres/gpu:  64G hpctpa3pc0037
       22457466_45  red rx_E09_probe  4475918  R       0:17    7:59:43   1   8 gres/gpu:  64G hpctpa3pc0038
       22457466_46  red rx_E09_probe  4475918  R       0:17    7:59:43   1   8 gres/gpu:  64G hpctpa3pc0057
       22457466_47  red rx_E09_probe  4475918  R       0:17    7:59:43   1   8 gres/gpu:  64G hpctpa3pc0058
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
