# HPC setup and operation

The default runner targets the environment supplied for the hackathon: Moffitt's SLURM `red` partition, one NVIDIA A30 with 24 GB VRAM, 32 GB host memory, a four-hour time limit, and the `Anaconda3/2024.02-1` module. It creates a fresh Python 3.11 environment with vLLM 0.10.2, PyTorch 2.8.0/CUDA 12.8, Transformers 4.55.2, and Hugging Face Hub 0.34.4. Direct dependencies are pinned in `requirements-vllm.txt`; transitive dependencies are resolved during setup and recorded in `.state/requirements-resolved.txt`.

The pinned GPU environment requires Linux `x86_64` with glibc 2.28 or newer. These requirements come from the binary wheels selected by the runner; the bootstrap checks them before installation. The local mock runner has no GPU-wheel requirement.

The model snapshot is pinned to `nvidia/Nemotron-Mini-4B-Instruct` revision [`791833e92ebddb0bc2c1007f6d2b6764f886a2ae`](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct/commit/791833e92ebddb0bc2c1007f6d2b6764f886a2ae). This repository publishes a PyTorch binary checkpoint, which the preparation command downloads alongside its tokenizer and configuration. Consult the [model card and license](https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct) when using or redistributing the weights.

## Submit an experiment

```bash
bash run_hpc.sh
```

The submission command prints the SLURM job identifier; returning from submission does not mean the experiment has completed. Check the corresponding `logs/slurm-<jobid>.out` and `.err` files. Default experiment results are saved under `results/hpc-<jobid>/`.

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
