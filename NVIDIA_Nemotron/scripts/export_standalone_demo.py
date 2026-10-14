#!/usr/bin/env python3
"""Export a verified synthetic handoff UI bundle as one offline HTML file."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('handoff_viewer', ROOT / 'demo/handoff_app.py')
viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)


def export(bundle_dir, output):
    bundle = viewer.load_bundle(bundle_dir)
    patients = []
    for pid, patient in sorted(bundle['patients'].items()):
        assets = {}
        for (kind, fmt), entry in patient['assets'].items():
            mime = 'image/png' if fmt == 'png' else 'application/pdf'
            assets[kind + '_' + fmt] = 'data:' + mime + ';base64,' + base64.b64encode(entry['path'].read_bytes()).decode()
        result = patient['result']
        # Export only useful provenance; omit machine-specific paths and raw logs.
        patients.append(dict(id=pid, scores=patient['scores'], label=patient['actual_response'],
            outcome=viewer.outcome_label(patient['scores']['fused'], patient['actual_response']),
            narrative=result['narrative'], source=result['narrative_source'], source_label=viewer.SOURCE_TEXT[result['narrative_source']],
            quality=result['quality'], review_required=result['review_required'], limitations=result['limitations'],
            context=result['clinical_context'], analysis=patient['analysis'], audit=patient['audit'],
            warnings=list(dict.fromkeys(patient['warnings'] + [w for a in patient['assets'].values() for w in a.get('warnings', [])])),
            clinical_plot_mismatch=patient['clinical_plot_mismatch'], mif_score=patient['mif_score'], assets=assets,
            provenance={k: result['provenance'].get(k) for k in ('prompt_version', 'prompt_sha256', 'backend')},
            predictions=result['predictions']))
    payload = dict(patients=patients, exported_at=bundle['ui_export_manifest'].get('exported_at_utc'),
                   input_sha256=bundle['ui_export_manifest'].get('source_input_sha256'))
    serialized = json.dumps(payload, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'demo/standalone_template.html').read_text()
    html = template.replace('/*__PATIENT_DATA__*/', serialized)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')
    print(json.dumps({'output': str(path.resolve()), 'patients': len(patients), 'bytes': path.stat().st_size,
                      'sources': sorted({p['source'] for p in patients})}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle-dir', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    export(args.bundle_dir, args.output)
