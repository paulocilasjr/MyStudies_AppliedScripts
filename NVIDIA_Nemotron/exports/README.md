# Shareable patient explorer

Send `ICB_Patient_Explorer.html` as a single file. The recipient saves it and double-clicks it to open in a browser. No installation, internet connection, server, or adjacent files are needed. JavaScript must be enabled.

The snapshot contains all five synthetic patients from `nim-demo-20261014T152515Z`: corrected handoff-v3 scores and figures, saved narratives from NVIDIA’s hosted `nvidia/nemotron-3-ultra-550b-a55b`, and the remaining evidence warnings. All five reports passed the existing output checks. The corrected clinical PNG labels have no discrepancies in the recorded partial checks, and the alternate mIF scores were removed by the producer. Attention weights are still not tile response probabilities. Patient selection is local; it does not generate new predictions or narratives.

To rebuild from another completed handoff UI bundle, run from the project root:

```bash
python3 scripts/export_standalone_demo.py \
  --bundle-dir results/nim-demo-20261014T152515Z/ui \
  --output exports/ICB_Patient_Explorer.html
```

The exporter validates the bundle using the existing viewer loader, embeds images and PDFs, and omits machine-specific model paths. The HTML has no external dependencies and blocks network connections through its content security policy.

To regenerate the narratives through NVIDIA and refresh this file, run `python3 scripts/run_nim_demo.py`. It requests the API key through hidden terminal input; no key is embedded in the HTML.
