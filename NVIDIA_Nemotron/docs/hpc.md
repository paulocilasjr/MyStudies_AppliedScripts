# HPC setup and operation

The default runner targets the environment supplied for the hackathon: Moffitt's SLURM `red` partition, one NVIDIA A30 with 24 GB VRAM, 32 GB host memory, a four-hour time limit, and the `Anaconda3/2024.02-1` module. It creates a fresh Python 3.11 environment with vLLM 0.10.2, PyTorch 2.8.0/CUDA 12.8, Transformers 4.55.2, and Hugging Face Hub 0.34.4. Direct dependencies are pinned in `requirements-vllm.txt`; transitive dependencies are resolved during setup and recorded in `.state/requirements-resolved.txt`.

The pinned GPU environment requires Linux `x86_64` with glibc 2.28 or newer. These requirements come from the binary wheels selected by the runner; the bootstrap checks them before installation. The local mock runner has no GPU-wheel requirement.

The model snapshot is pinned to `nvidia/Nemotron-Mini-4B-Instruct` revision [`791833e92ebddb0bc2c1007f6d2b6764f886a2ae`](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct/commit/791833e92ebddb0bc2c1007f6d2b6764f886a2ae). This repository publishes a PyTorch binary checkpoint, which the preparation command downloads alongside its tokenizer and configuration. Consult the [model card and license](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct) when using or redistributing the weights.

## Submit an experiment

```bash
bash run_hpc.sh
```

The submission command prints the SLURM job identifier; returning from submission does not mean the experiment has completed. Check the corresponding `logs/slurm-<jobid>.out` and `.err` files. Default experiment results are saved under `results/hpc-<jobid>/`.

## Run synthetic patients through the real GPU model

The synthetic fixture is mock **input data**. The following command uses the real vLLM/Nemotron backend, downloads the pinned public model when needed, generates narratives on the allocated A30, and verifies the completed run:

```bash
bash run_hpc.sh --smoke
```

Default smoke results are written to `results/gpu-smoke-<jobid>/`. The final `verify-run` step checks input identity, patient counts and IDs, unchanged scores and modality availability, review flags, source metadata, and synthetic-data declarations. It requires the real vLLM backend and all four synthetic records to have `narrative_source="vllm"` with `quality.status="passed"`. Any fallback, injected test generator, or mock result fails this strict acceptance gate. The report records `all_generated_narratives_accepted`. Every narrative still requires human review; verification does not establish clinical correctness.

Smoke verification also requires the recorded model ID and revision to match `HPC_MODEL_ID` and `HPC_MODEL_REVISION`. At defaults, these identify the pinned Nemotron snapshot above. A custom `--model-path` must contain matching preparation metadata; an unrecorded or mismatched snapshot cannot pass the verified smoke test. Ordinary experiments can still use local directories with unrecorded revision metadata. Manifest matching checks the recorded identity, not cryptographic hashes of every weight file.

Verification writes `verification.json` into the completed run directory. If inference completes but acceptance fails, the published artifacts remain for diagnosis and the SLURM job exits nonzero. Look for `GPU smoke verification passed` in stdout and inspect the verification report. Submission success, a doctor pass, and coherent deterministic fallback text each provide less evidence than this completed smoke run.

Use a fresh output path for every attempt:

```bash
bash run_hpc.sh --smoke --offline --output-dir results/gpu-smoke-001
```

Smoke mode uses only `examples/mock_predictions.jsonl`; it rejects `--input`, `--prepare-only`, non-experiment commands, and hidden backend/input/output/model overrides after `--`. The runner's `--model-path` and `--output-dir` controls remain available. Generation options such as `-- --max-tokens 300` can be forwarded. Use a normal experiment with `--input` for the eventual team records.

The local command `bash scripts/run_local.sh` remains a deterministic CPU/mock test and does not load or download Nemotron.

Use a specific input and output location when integrating team predictions:

```bash
bash run_hpc.sh --offline \
  --input /share/lab_goecks/Alyssa/Markowitz/feb2026/results/predictions/copilot_input.jsonl \
  --output-dir /share/lab_goecks/Alyssa/Markowitz/feb2026/results/copilot/run-001
```

Inputs and outputs may contain patient-level context. Keep them within the study's approved HPC storage and use pseudonymous study IDs. The tracked `examples/` files are entirely synthetic. `.gitignore` excludes the default data, environment, cache, model, log, and result directories.

## Separate preparation from inference

First-time environment creation downloads public software; model preparation downloads public weights. Run preparation on a node where the site permits that network access:

```bash
bash run_hpc.sh --prepare-only
```

Then submit the experiment with network-dependent preparation disabled:

```bash
bash run_hpc.sh --offline
```

For the verified real-model smoke test after this preparation, submit `bash run_hpc.sh --smoke --offline`. The environment and cache must reside on a filesystem visible to both the preparation node and the GPU node.

`--offline` requires a prepared environment and complete local model snapshot. It fails with a diagnostic if either is missing. All real-model inference loads the local path with offline settings, including inference performed after normal preparation. There is no hosted LLM fallback.

Runner files stay relative to the copied repository by default:

| Location | Contents |
| --- | --- |
| `.envs/nemotron-vllm/` | Isolated inference environment. |
| `.cache/huggingface/` | Public model cache. |
| `.state/` | Setup state and model snapshot metadata. |
| `logs/` | SLURM output and error logs. |
| `results/` | Experiment artifacts. |

If using a model directory prepared elsewhere on the HPC:

```bash
bash run_hpc.sh --offline --model-path /approved/local/model/snapshot
```

A local snapshot must contain the tokenizer, configuration, and weight files. Copying an isolated model weight file is insufficient. Avoid a symlink-based Hugging Face snapshot whose backing `blobs/` directory was left behind during transfer.

The selected checkpoint alone is about 8.4 GB. The isolated Python environment, CUDA/PyTorch dependencies, package caches and temporary downloads require additional storage; confirm sufficient quota on the shared filesystem before preparation. A laptop-created macOS conda environment cannot be copied as the Linux GPU environment.

## Configure the site

The runner accepts a trusted shell configuration at `config/hpc.env`, or an explicit path with `--config`. Start from `config/hpc.env.example`. Keep local configuration out of version control. Because this file is sourced by the shell, use a configuration you control.

```bash
bash run_hpc.sh --config config/hpc.env
```

Use the documented variables in the example configuration to override module names, environment and cache paths, SLURM resources, and model selection. Changing the pinned runtime or model revision creates a new experiment configuration and should be reflected in run provenance.

## Driver and CUDA compatibility

The runner requires an NVIDIA Linux driver of at least 570.26 for its native CUDA 12.8 runtime. NVIDIA lists that driver version for CUDA 12.8 in its [release notes](https://docs.nvidia.com/cuda/archive/12.8.0/cuda-toolkit-release-notes/index.html). Loading the supplied CUDA 13 toolkit module does not upgrade the driver or make arbitrary binary wheel combinations compatible. The runner purges site CUDA/PyTorch modules by default and uses its own environment. vLLM recommends an isolated environment and ties binary compatibility to its PyTorch/CUDA build; consult the [vLLM 0.10.2 GPU installation guidance](https://docs.vllm.ai/en/v0.10.2/getting_started/installation/gpu.html).

The chosen model's weights alone do not determine GPU memory use: the KV cache, configured context length, batching, and runtime buffers also consume VRAM. Start with the runner's conservative settings on the A30. If loading fails, capture `nvidia-smi`, the doctor output, and the relevant SLURM log before changing pins or memory settings.

```bash
bash run_hpc.sh --command doctor
```

The doctor command reports the environment and device state. It does not substitute for an actual model-generation experiment.

Doctor checks total device memory rather than available memory and does not initialize the model, chat template, guided decoding, or complete KV cache. The real smoke experiment must qualify those paths on the allocated node. If the driver or host runtime is incompatible, involve the HPC team rather than changing pins until imports happen to succeed.

## Access required to execute on Moffitt

Execution needs an authenticated, site-approved login connection, any required VPN/MFA or jump host, the shared destination directory and write permission, and any SLURM account/QOS required to request `red`/A30 resources. Public package/model access must be available on the preparation node, or the site must provide an approved prepopulated environment/cache. The login and GPU hosts must meet the selected Linux/glibc/runtime requirements.

No password, private key, or MFA code belongs in this repository. Authentication is completed through the site's normal client/session. Until that connection and allocation are available, local mocked scheduler tests cannot establish that the HPC model has loaded or generated text.

## Use an already allocated GPU session

```bash
srun --partition=red --gres=gpu:a30:1 --mem=32G --time=4:00:00 --pty bash
bash run_hpc.sh --direct --offline
```

`--direct` executes inside the current allocation without another `sbatch`. The standard runner otherwise submits the job for you.

## Serve the copilot for the demo

```bash
bash run_hpc.sh --command serve --offline -- --host 127.0.0.1 --port 8000
```

The API listens on loopback. Run the UI on the same node or use a site-approved SSH tunnel to that compute node. The endpoint is a local research service, with no authentication layer or internet exposure configured by this project. See [the integration contract](integration.md) for request examples.

The provided Singularity runtime remains available as a site-level alternative, but this implementation's one-command path uses the isolated conda environment. A generic NVIDIA PyTorch container is not a ready-to-run NIM server or a complete copilot environment.
