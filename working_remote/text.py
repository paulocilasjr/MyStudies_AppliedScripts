https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ conda activate compass-foundation-test
ning/third_party/COMPASS}"
source "$TEST_CODE_DIR/config/settings.env"

git -C "$COMPASS_SOURCE_DIR" rev-parse --short HEAD
for input in "$COMPASS_SOURCE_DIR/.git" "$COMPASS_WEB_SOURCE_DIR/.git" \
  "$COMPASS_GENE_ORDER" "$COMPASS_GENE_MAP" "$COMPASS_GTF"; do
  [[ -e "$input" ]] || printf 'MISSING %s\n' "$input"
done
[[ -n "$COMPASS_STAR_INDEX_DIR" && -s "$COMPASS_STAR_INDEX_DIR/Genome" ]] ||
  printf 'MISSING compatible STAR index in COMPASS_STAR_INDEX_DIR\n'
command -v "$COMPASS_RSCRIPT" || printf 'MISSING Rscript\n'

PUBLIC_COHORT_SET=all16 TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
  bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"(compass-foundation-test) 4475918@hpctpa3pl0001:federated-lOURCE:-$PWD/compass_foundation_training/third_party/COMPASS}"O
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ source "$TEST_CODE_DIR/config/settings.env"
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ git -C "$COMPASS_SOURCE_DIR" rev-parse --short HEAD
9ecacfb
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ for input in "$COMPASS_SOURCE_DIR/.git" "$COMPASS_WEB_SOURCE_DIR/.git" \
>   "$COMPASS_GENE_ORDER" "$COMPASS_GENE_MAP" "$COMPASS_GTF"; do
>   [[ -e "$input" ]] || printf 'MISSING %s\n' "$input"
> done
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ [[ -n "$COMPASS_STAR_INDEX_DIR" && -s "$COMPASS_STAR_INDEX_DIR/Genome" ]] ||
>   printf 'MISSING compatible STAR index in COMPASS_STAR_INDEX_DIR\n'
MISSING compatible STAR index in COMPASS_STAR_INDEX_DIR
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ command -v "$COMPASS_RSCRIPT" || printf 'MISSING Rscript\n'
MISSING Rscript
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ PUBLIC_COHORT_SET=all16 TEST_MODEL_MANIFEST="${TEST_MODEL_MANIFEST:-$NEW_MODELS}" \
>   bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
ERROR: required COMPASS input is missing: /Genome
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ git pull
Already up to date.
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457467  red rx_E09_analy  4475918  R       6:14 1-23:53:46   1  16       N/A 128G hpctpa3pc0003
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
