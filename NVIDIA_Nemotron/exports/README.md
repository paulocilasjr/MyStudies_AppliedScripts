# Shareable patient explorer

Send `ICB_Patient_Explorer.html` as a single file. The recipient saves it and double-clicks it to open in a browser. No installation, internet connection, server, or adjacent files are needed. JavaScript must be enabled.

The snapshot contains all five synthetic patients from `local-mvp-20261014T050421Z`: scores, saved local Nemotron narratives, original PNG/PDF figures, and evidence warnings. It preserves the stale clinical-plot and alternate mIF-score warnings. Patient selection is local; it does not generate new predictions or narratives.

To rebuild from another completed handoff UI bundle, run from the project root:

```bash
python3 scripts/export_standalone_demo.py \
  --bundle-dir results/local-mvp-20261014T050421Z/ui \
  --output exports/ICB_Patient_Explorer.html
```

The exporter validates the bundle using the existing viewer loader, embeds images and PDFs, and omits machine-specific model paths. The HTML has no external dependencies and blocks network connections through its content security policy.
