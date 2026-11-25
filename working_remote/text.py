https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

conda activate compass-foundation-test
export COMPASS_SOURCE_DIR="${COMPASS_SOURCE:-$PWD/compass_foundation_training/third_party/COMPASS}"
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
  bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
