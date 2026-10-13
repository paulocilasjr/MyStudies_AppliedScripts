# First real Nemotron run with synthetic patients

The local CPU mock tests the data plumbing. This procedure downloads and runs the actual NVIDIA model on an A30 using four synthetic patients. No real patient data are needed. The responder endpoint is still undecided, so the fixture cannot establish clinical predictive performance.

## Transfer the current code

From the local project, `python3 scripts/package_hpc.py` creates `dist/nemotron-hpc-smoke.tar.gz` and its SHA-256 file. The package contains source, tests, documentation and explicitly named synthetic fixtures. It excludes patient inputs, generated results, site settings, credentials, environments and model caches.

Transfer both files through your existing authenticated HPC workflow to an approved shared location. For example, from your own Mac terminal with working SSH:

```bash
scp dist/nemotron-hpc-smoke.tar.gz dist/nemotron-hpc-smoke.tar.gz.sha256 \
  4475918@red.moffitt.org:/share/lab_goecks/Alyssa/Markowitz/feb2026/
```

In the HPC terminal, extract into a new directory to preserve any previous checkout:

```bash
cd /share/lab_goecks/Alyssa/Markowitz/feb2026
sha256sum --check nemotron-hpc-smoke.tar.gz.sha256
mkdir copilot-smoke-001
tar -xzf nemotron-hpc-smoke.tar.gz -C copilot-smoke-001
cd copilot-smoke-001/NVIDIA_Nemotron
```

Choose a new directory name if `copilot-smoke-001` already exists. All following commands run from the unpacked project root. If the site requires an account or QOS, first copy `config/hpc.env.example` to `config/hpc.env` and supply the site values.

## One command to prepare and submit

On an approved internet-connected preparation node:

```bash
bash run_hpc.sh --prepare-only && bash run_hpc.sh --smoke --offline
```

This installs the pinned Python environment and public model on shared storage, then submits a `red`/A30 SLURM job. The compute job uses local weights and offline inference settings. Preparation does not read patient inputs. If the site allows downloads on compute nodes, `bash run_hpc.sh --smoke` performs setup within the allocation instead.

The command prints a job number. Submission is not completion. Track it with:

```bash
COPILOT_JOB_ID=$(cat .state/last_job_id)
squeue -j "$COPILOT_JOB_ID"
tail -n 60 "logs/slurm-${COPILOT_JOB_ID}.out" "logs/slurm-${COPILOT_JOB_ID}.err"
sacct -j "$COPILOT_JOB_ID" --format=JobID,State,ExitCode,Elapsed
```

The job needs compatible Linux/glibc, the configured Anaconda module, shared storage/quota, native NVIDIA driver >=570.26 and a full A30 allocation. The runner reports incompatible prerequisites before inference; it cannot install the host GPU driver. See [HPC operation](hpc.md).

## Completion evidence and expected JSON

After successful generation, inspect:

```bash
cat "results/gpu-smoke-${COPILOT_JOB_ID}/verification.json"
cat "results/gpu-smoke-${COPILOT_JOB_ID}/manifest.json"
```

Acceptance requires `ok: true`, the configured model ID/revision, recorded native vLLM execution, four patients, unchanged supplied evidence and scores, complete artifacts, and `source_counts: {"vllm": 4}`. All four narratives must pass the implemented screen. Any fallback makes smoke acceptance fail while keeping completed experiment artifacts for diagnosis. An initialization/generation failure may leave only the SLURM logs.

`narratives.jsonl` contains one full JSON object per patient with predictions, feature evidence, clinical context, interpretation text, comparison, limitations, review status, quality and provenance. It preserves the clinical-only patient as well as the three complete multimodal cases. Screening and execution acceptance do not verify clinical correctness.

## Export for Junhao's current UI

After the completed run:

```bash
PYTHONPATH=src .envs/nemotron-vllm/bin/python -m nemotron_copilot export-ui \
  --run-dir "results/gpu-smoke-${COPILOT_JOB_ID}" \
  --output-dir "results/ui-smoke-${COPILOT_JOB_ID}"
```

With a custom environment prefix, use its Python executable instead. The UI bundle contains a prediction CSV for the three complete cases and `narratives.json` mapping those IDs to narrative text. Labels remain blank for these synthetic inputs. The clinical-only case remains in the complete structured sidecar and is listed as excluded from the current UI, which requires all three scores. [UI integration](demo_ui.md) explains the exact directory layout and launch command.

## Readiness at handoff

The local synthetic pipeline, output contract, compatibility exporter and automated tests have been checked. The audited UI loader accepts the exported file contract. Actual Streamlit rendering and an HPC model download/load/generation have not been executed from this workspace. The configured SSH host was reachable but noninteractive authentication was rejected; this runbook supports the requested execution in your existing HPC terminal.
