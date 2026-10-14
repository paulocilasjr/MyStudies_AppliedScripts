# Project context for the ICB interpretation skill

This reference is for people who maintain the skill or review its narratives. **It is not loaded into the model prompt.** Nemotron-Mini-4B has a 4,096-token context, and longer prompts measurably degraded its replies (see [Maintaining the skill](#maintaining-the-skill)). The model receives a one-paragraph summary: the `Project:` paragraph in `SKILL.md`.

## Foundation study

Pybus A, Kirchgaessner R, Nguyen J, Moran Segura C, Morais Lyra Jr PC, Rose T, Gray J, Goecks J, Markowitz J. *Predicting anti-PD-1 immune checkpoint blockade response in melanoma patients with spatially aware machine learning models.* npj Precision Oncology 10, 56 (2026). <https://doi.org/10.1038/s41698-025-01250-8>. Data: Zenodo [10.5281/zenodo.16898362](https://doi.org/10.5281/zenodo.16898362). Code: [goeckslab/Melanoma-ICB-mIF](https://github.com/goeckslab/Melanoma-ICB-mIF).

**Cohort.** Twelve stage IV melanoma patients at Moffitt received anti-PD-1 monotherapy (pembrolizumab or nivolumab). Tissue was collected by resection or core biopsy 1–12 months before treatment.

| Group | Patients | Response definition |
| --- | ---: | --- |
| Responders | 4 | RECIST complete or partial response, with progression-free survival over 600 days |
| Non-responders | 8 | Progression within 161 days |

**Tissue assay.** Two 8-plex multiplex immunofluorescence (mIF) panels were used:

| Panel | Markers |
| --- | --- |
| Lymphoid | CD3, CD8, CD20, PD-L1, LAG-3, SOX10, iNOS, nNOS |
| Myeloid | CD11c, CD14, CD34, MHCII, N-Cadherin, SOX10, iNOS, eNOS |

The lymphoid panel covered about 8.25 million cells. Slides were cut into 1 mm² tiles: 699 from responders and 983 from non-responders. Marker-negative cells were labelled "stromal" (43–52% of cells).

**Features**:
- Cell-state proportions (22 lymphoid states).
- Marker proportions within subpopulations.
- Proximity scores: cell-pair counts within 20, 30, 60 and 90 µm.
- Ripley's L clustering and repulsion between cell states.
- Recurrent cellular neighborhoods (RCNs): k-means clusters of 60 µm neighborhoods.

**Findings**:
- **No single biomarker:** no single feature, including PD-L1 positivity, separated responders from non-responders at the patient level. After false-discovery correction, mixed-effects models found one significant feature. Ripley's L clustering between CD3+ iNOS+ cells and CD3+ CD8+ PD-L1+ cells was greater in non-responders.
- **Heterogeneous responders:**
  - Two responders were "immunoreactive", with high PD-L1+ and CD8+ proportions.
  - Two were "immune-cold" and resembled non-responders.
  - All non-responders were immune-cold.
  - No tertiary lymphoid structures were observed.
- **TIL-like niche:** a tumor-infiltrating-lymphocyte-like neighborhood (RCN8: CD8, LAG-3, PD-L1, SOX10, iNOS) was most abundant in three of four responders.
- **Nitric oxide synthase:** iNOS expression in cytotoxic T cells was associated with response. The authors note that iNOS also has a literature history as a poor prognostic factor.
- **Models:**
  - LightGBM with leave-one-patient-out cross-validation, repeated 100 times.
  - ROC AUC was 0.59 for compositional features, 0.63 with spatial features added, and 0.76 for an "Immune-High" model restricted to tiles with at least 2% CD8+ cells (specificity 0.65).
  - Majority vote over tiles classified 11 of 12 patients correctly. The miss was a non-responder core biopsy with six qualifying tiles.

**Stated limitations**:
- Only four responders.
- Responder heterogeneity.
- Mixed collection sites (skin, intestine, lung, lymph node) and mixed resections and biopsies.
- An undefined "stromal" population.
- Few markers per panel.

## This project: the hackathon extension

**Research question.** Predict ICB responders versus non-responders.

**Modalities.** Multiplex immunofluorescence and clinical data. H&E images may be added later, pending a collaborator's data drop-off, and are not used now.

**Status.**
- 48 patients have clinical data; 29 of them also have mIF data.
- About 10 more patients may be available, but with large batch effects, probably beyond the hackathon's scope.

**Proposal.** Build and test three models, each scored separately and supplied to this copilot:
1. A clinical-only model.
2. An mIF-only model.
3. A late-fusion model.

**Current synthetic handoff (`examples/paulo_handoff/`).** The producer reports these models. Their aggregate metrics are producer claims and are not reproduced here:

| Model | Design | Reported AUC |
| --- | --- | ---: |
| mIF | Gated-attention multiple-instance learning over tiles; about 1,500 parameters; 7 spatial/compositional and 3 biopsy-site features; CD8 ≥ 0.01 tile filter (echoing the Immune-High finding) | 0.81 |
| Clinical | XGBoost (100 trees, depth 5) on 5 clinical features | 0.77 |
| Fusion | Bayesian product rule of the two scores, no trained parameters | 0.88 |

The metrics come from 5-fold cross-validation over 10 seeds on 27 patients, which differs from the paper's leave-one-patient-out design. The five handoff patients (S01–S05) and their labels are synthetic.

## Reading the evidence fields

| Field | Meaning | What it does **not** mean |
| --- | --- | --- |
| `probability` | Model score for the responder class | A calibrated individual probability (calibration is unknown) |
| `decision_threshold` | Producer-declared cut-off for a responder display class | A clinically validated threshold |
| Clinical SHAP attribution | The feature's contribution to this score, on the stated scale | A cause, or biological evidence |
| mIF attention contrast | Difference in a feature between the tiles the model weighted most and least | A signed effect on the score, or a tile response probability |
| Ripley's L, proximity score | Spatial clustering of, or distance between, two cell states in a tile | Cell–cell interaction or mechanism |
| Fused score | Deterministic combination of the clinical and mIF scores | Independent evidence, or proof that fusion performs better |
| Missing mIF or fused score | No tissue data, or no fusion for this patient | Evidence of anything; it is never imputed |

**Implications for reviewers** (not given to the model):
- Clinical–mIF disagreement is expected for some true responders, because immune-cold responders resembled non-responders in tissue.
- When both inputs agree, the product rule pushes the fused score further toward their shared side.
- None of this cohort evidence is validated for clinical decisions.

## The structured patient report

Each result's `narrative` is a four-part report (`report.render_report`). The application prints every number, list and literature note; the model writes only the prose after each dashed line and the conclusions.

```text
Patient S03 report:

1) Model evaluation predictions:
Clinical model score = 0.1142
Spatial mIF model score = 0.7966
Fused model prediction score = 0.3355
------------------------ <model: what the scores mean; the strongest hypothesis or the conflict and tendency>

2) Clinical evaluation:
Clinical features towards responder = <features with positive SHAP, strongest first, with value and SHAP>
Clinical features towards non-responder = <features with negative SHAP>
------------------------ <model: which features push which way, next to their literature gist>
Literature notes:
<feature>: <curated note> (<source>)

3) Immune evaluation:
<mIF feature> (value; higher or lower in the tiles the mIF model weighted most, contrast): <curated note> Classification: <literature direction>. (<source>)
Attention contrasts show where the mIF model focused; they are not signed effects on the score.

4) Conclusions:
<model: strongest hypothesis, or what conflicts or is missing and the tendency; cautions>

Research output requires independent clinical review and does not establish treatment benefit.
```

**Strongest hypothesis.** The hypothesis is computed by the application (`report.hypothesis`), never chosen by the model:

| Situation | Strongest hypothesis |
| --- | --- |
| Clinical, mIF and fused scores on the same side of their thresholds | That side; "uneven" when the clinical and mIF scores differ by at least the disagreement threshold |
| Clinical and mIF on opposite sides | No strong hypothesis; the tendency is the fused score's side |
| One modality missing | A weak hypothesis from the available score; missing scores are never inferred |
| No thresholds supplied | No side is assigned |

**Curated literature (`feature-literature.json`).** Each entry matches supplied feature names and carries four things:
- a one-line `gist` for the model (clinical features);
- a full `note` printed in the report;
- the literature `direction`;
- its `sources`, with full citations in the same file.

Entries cover the clinical and mIF features the team's models currently emit. A feature without an entry is printed with "No curated literature note". Review each note against its source before using it in a manuscript; add an entry when a model gains a new feature.

## How the skill produces the prose

1. **One focused prompt per report part.** `SKILL.md` has shared instructions (role, project summary, safety) and one section per part. `prompts.py` builds three short system prompts of about 1,200 tokens each, one per part (`prediction_summary`, `clinical_interpretation`, `conclusion`). Each conversation returns only `{"text": "..."}`. A single prompt for all three parts (about 3,100 tokens) produced copied, contradictory prose; per-part prompts did not.
2. **The case as each part sees it (`report.model_payload`).** Every value is plain words without digits:
   - `situation`: each model's threshold side and margin;
   - `hypothesis`: the computed hypothesis;
   - `clinical_evidence`: the three strongest clinical features, each with its push direction and literature gist.

   The score and conclusion parts see `situation` and `hypothesis`; the clinical part sees `clinical_evidence`. Free-text clinical context is not sent. The 4B model restates words reliably; it misreads class flags and numbers in JSON.
3. **Worked examples (`prompt-examples.json`).** There is one per situation: agreement on either side, uneven support, conflict with each tendency, and a single modality. Each part's prompt shows only its inputs and text from every example. `source_evidence` keeps the synthetic scores and features, from which tests rebuild the inputs and run the screen.
4. **The report screen (`copilot.screen_report`).** It checks:
   - JSON shape, section length, numbers, markup, and treatment or certainty language;
   - acknowledgment of disagreement and missing modalities.

   `report_contradictions` also rejects prose that contradicts the computed facts:
   - a model on the wrong side of its threshold, or a wrong fused side;
   - a hypothesis or tendency other than the computed one;
   - agreement asserted across a threshold split;
   - a supplied modality called missing;
   - a clinical feature pushing against its attribution, given a direction without one, or described as lacking a direction it has.

   If any part is rejected, all three are replaced by deterministic prose built from the same facts and labelled `fallback`.

## Maintaining the skill

Rules learned from local evaluation with the pinned model (details in [prompt review](../../../../../docs/prompt_review.md)):

- **Keep each prompt short and single-purpose.** A version with this full context and a banned-word list (3,687 prompt tokens) dropped acceptance to 2 of 15 synthetic cases; replies grew long and introduced numbers and invented biology. One prompt for all three report parts (about 3,100 tokens) accepted 7–11 of 15. One short prompt per part accepted 15 of 15.
- **Do not list forbidden words in the prompt.** Small models echo them ("high", "predicts", "non-responder").
- **Give each comparison situation its own example, and keep copied phrases true for any case.** The model copies the closest example; a situation-specific caveat or a "consistent with the literature" claim copied into the wrong case becomes a false statement. Examples therefore place each feature's push next to its literature gist without asserting that they agree.
- **Keep facts out of the model's hands.** Scores, feature lists, literature notes and the hypothesis are deterministic; the screen checks every side, direction and hypothesis the prose states.
- **Avoid example features that collide with test cases of the opposite kind.** An unsigned "LDH level" example led the model to deny the signed LDH attribution of another case; the screen now rejects that, and the unsigned example uses a different feature.
- **Rebuild examples after editing them or the literature.** Edit `source_evidence` or `output` in `prompt-examples.json`, or a gist in `feature-literature.json`, then run `PYTHONPATH=src python3 scripts/build_prompt_examples.py`; it refreshes each example's derived input and refuses to write examples that fail the screen.
- **Re-run the evaluation and tests after every change.** Run `PYTHONPATH=src .envs/local-mvp/bin/python scripts/evaluate_prompt.py` and the unit tests. Any change to the skill or examples changes the recorded prompt SHA-256; bump `PROMPT_VERSION` for meaningful changes.
