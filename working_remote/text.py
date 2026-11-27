 I've built the core profile, step 1 of your order, as a new HPC_data_pipeline/ suite. It passes 28 unit tests on
  synthetic fixtures, but it hasn't been run on the cluster or against your real TCGA/GTEx inputs yet. Your message
  matches the feedback I'd already turned into the revised plan, so the order stands: core first, then the ICI registry,
   with recount3 waiting for an ADR.

  What the core profile does:

  • Default profile reproduces today's inputs. core uses galaxy = TCGA and anvil = GTEx, with the existing processed
  TSVs, training config, split seed and protocol. It first checks the hash, gene order, row counts and cancer codes of
  those TSVs. Then it runs the existing 01_prepare_clients.py, 02_aggregate_scaler.py and 01_prepare_unified_memmap.py
  unchanged.
  • The core-reproduce stage must pass. It compares the result with today's centralized memmap and federated clients on
  sample list, gene order, contexts and training indices. It also checks that both views hold the same samples, and
  writes a file-by-file comparison.
  • core-rebuild is a separate profile. It re-downloads TCGA (one Slurm array element per GDC project) and GTEx with the
   existing builders, and only reports differences against today's inputs.
  • Stages check their own outputs. A stage fails on missing or empty files, zero rows, unexpected counts, gene-order
  drift, or an input that changed after it was verified. It refuses to start over files in its output folders that no
  finished run recorded, which covers the stale report.md case.
  • Resuming checks hashes, not just whether files exist. submit skips stages whose outputs still match, and resubmits
  only the unfinished elements of an array stage.
  • HPC lessons are built in. site.env.example sets the CA-bundle exports and the separate compass-data Rscript. plan
  checks free space and records a quota command's output.
  • Lineage. manifests/sample_lineage.tsv has one row per sample: GDC file IDs and URLs or GTEx sample ID, checksum,
  builder script, client, split, role and profile. dataset_manifest.json records the hashes of everything else.

  On the canonical directory: both names are correct but mean different things. compass_hpc_foundation_model_test holds
  the code. /share/.../compass_foundation_model_test is that suite's data root, where E13's dataset lives.

  repo.py check passes for the new suite. I also registered it in config/repository.json and regenerated
  docs/repository-layout.md. Two kinds of errors remain on this Windows checkout, the same family as the pre-existing
  ones. Shell-syntax checks fail because Windows bash can't resolve the paths. Compatibility symlinks are reported
  missing because the checkout has no symlinks. I haven't committed anything.

  To run it on HPC:

  1. Fill in inputs.* in config/profiles/core.json (your existing COMPASS_dataset, TCGA_dataset, GTEx_dataset folders).
  2. Fill in reference_targets.* with today's UNIFIED_DATA_DIR and FEDERATED_SEED_DATA_ROOT.
  3. Source a copy of site.env.example, then run:
       python HPC_data_pipeline/prepare_data.py plan --profile core
       python HPC_data_pipeline/prepare_data.py submit --profile core --dry-run

     If the dry run looks right, submit without --dry-run.

  Next, step 2: the ICI registry with a role and first-use record for each cohort, tested ID maps per cohort, a label
  check against iAtlas/TIGER, and the clinical merge with a correlation-based near-duplicate check. After that, GDC
  extras mapped onto existing cancer codes.

  For E13, paste the collector output once jobs 22568363 and 22568364 finish, and I'll finish its section.


  Step 2 is built, but no new ICI cohort or GDC project is merged yet: each needs your review before it joins. The code
  only plans and tests locally so far. All 59 pipeline tests pass, and the 31 reviewer-experiment tests still pass (7
  skipped) with no reviewer code touched. repo.py check reports only the Windows-checkout shell-path and symlink errors
  from before.

  ici profile (new fine-tuning cohorts):

  • Registry (config/ici_registry.json). It lists all 16 released cohorts with patient and responder counts, which a
  test checks against benchmark.json. Each cohort records its prior roles by experiment, which settles the "independent
  confirmation" question E13 couldn't answer:
    • The original eight were used in the COMPASS release, core-8 (E01–E12) and E13.
    • The added eight were first used in E13.
  • Duplicate guard. Ravi 2023 is already present as SU2CLC1/2, which benchmark.json lists as aliases. The registry
  check rejects re-adding a released cohort or alias and flags any shared accession, such as Liu/Allen's phs000452.
  • Stage order:
    1. Hash-verify ALL16 without touching it.
    2. Inspect candidates: download the GEO files and list the response and timepoint fields.
    3. Build: TPM on COMPASS genes, R/NR labels, an ID join that fails if any labeled patient has no expression, and the
   registry's expected counts.
    4. Label check against iAtlas/TIGER; unchecked labels need explicit permission.
    5. Correlation-based near-duplicate check against the release and between new cohorts.
    6. Merge into a separately named dataset where release rows stay byte-identical.
  • ID maps. Per-cohort rules cover prefixes, zero-padding and arm suffixes. Two IDs collapsing to one key is an error,
  and every configured cohort must record real ID examples that the tests replay.

  core-gdc profile (GDC extras on existing cancer codes):

  • Downloads and inspection: all listed projects are downloaded with the existing GDC script and their metadata values
  listed.
  • Mapping: a project joins only after you fill in its map to an existing TCGA code and set reviewed_by. Maps to codes
  outside cancer_code.json are refused at plan time.
  • TCGA rules apply: no normals, no prior treatment, no FFPE, TPM averaged per patient. Excluded samples get a recorded
   reason.
  • TCGA near-duplicates: any GDC patient that correlates too closely with a TCGA tumor must be resolved before pooling,
   and TCGA always wins (the CPTAC case you raised).
  • core is unchanged. A test confirms it still maps only TCGA and GTEx.

  What needs you:

  • Jung2019 (GSE135222) and Cho2020 (GSE126044) are candidates only, so the first ici run just inspects them. I
  couldn't confirm their files or field names from here. After that run, fill in the file, unit, label field and map,
  expected counts and real ID examples from inspection.json, then mark them configured.
  • Braun 2020 needs its supplement URLs.
  • IMmotion151, JAVELIN, OAK/POPLAR and IMvigor010 are controlled-access stubs.
  • GDC maps all ship empty. suggested_map entries are guidance only; TARGET-AML/BEAT AML → LAML in particular is a
  scientific call for you to make.
  • Label check references: label_references needs iAtlas/TIGER label files with cohort, sample_id and response_label
  columns.

  Bugs found while building:

  • A smoke plan of ici with the real registry treated the profile's note key as a label file; fixed.
  • A test assertion in the GDC tests was wrong; fixed.

  I haven't committed anything. For E13, paste the collector output once jobs 22568363 and 22568364 finish.
