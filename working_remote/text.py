https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457467  red rx_E09_analy  4475918  R      12:09 1-23:47:51   1  16       N/A 128G hpctpa3pc0003
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ rx_rscript=$(conda run -n compass-data which Rscript) &&
>   export COMPASS_RSCRIPT="$rx_rscript" &&
>   "$COMPASS_RSCRIPT" --version
OHORTS=""
unset PUBLIC_RUN_TABLE PUBLIC_COMPASS_DIR PUBLIC_ITRP_RAW_DIR PUBLIC_ITRP_PROCESSED_DIR
source "$TEST_CODE_DIR/config/settings.env"
export CLINICAL_DATASET_ALL16="$PUBLIC_ITRP_PROCESSED_DIR"

if [[ -z "${SYNAPSE_AUTH_TOKEN_FILE:-}" && -s "$HOME/.config/synapse/compass_pat" ]]; then
  export SYNAPSE_AUTH_TOKEN_FILE="$HOME/.config/synapse/compass_pat"
fi
/usr/bin/which: no Rscript in (/home/4475918/.cargo/bin:/home/4475918/.conda/envs/compass-data/bin:/app/eb/software/Anaconda3/2024.02-1/condabin:/home/4475918/bin:/app/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/dell/srvadmin/bin:/cm/shared/apps/slurm/current/bin:/home/4475918/.local/bin:/home/4475918/bin)

ERROR conda.cli.main_run:execute(124): `conda run which Rscript` failed. (See above for error)
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export PUBLIC_DOWNLOAD_FASTQ=0 PUBLIC_MIN_COHORTS=16 PUBLIC_COHORTS=""
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ unset PUBLIC_RUN_TABLE PUBLIC_COMPASS_DIR PUBLIC_ITRP_RAW_DIR PUBLIC_ITRP_PROCESSED_DIR
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ source "$TEST_CODE_DIR/config/settings.env"
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ export CLINICAL_DATASET_ALL16="$PUBLIC_ITRP_PROCESSED_DIR"
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -z "${SYNAPSE_AUTH_TOKEN_FILE:-}" && -s "$HOME/.config/synapse/compass_pat" ]]; then
>   export SYNAPSE_AUTH_TOKEN_FILE="$HOME/.config/synapse/compass_pat"
> fi
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
>   bash "$TEST_CODE_DIR/scripts/submit_public_pipeline.sh"
Public continuous pipeline: 22457666
Run tag:                   public_all16_e13_20261125_020600Z
Download raw FASTQ:        0
Logs:                      /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/logs/public_all16_e13_20261125_020600Z
Final prepared dataset:    /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/data/processed/public_ITRP/public_all16_e13_20261125_020600Z
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
