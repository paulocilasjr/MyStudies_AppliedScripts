# Research evaluation and narrative review

The research question is whether clinical and mIF information help predict the study's ICB responder label. This component summarizes already-computed scores. Narrative fluency and a successful GPU run do not validate either the prediction models or a clinical endpoint.

## Define the endpoint before interpretation

Record the actual responder definition, assessment window, labeling source, and relevant treatment population in the upstream study documentation. Put the short definition into each input's `response_definition`. Until it is supplied, the copilot must preserve that uncertainty. Do not treat an unspecified label as equivalent to response at any particular time point, survival benefit, or a treatment recommendation.

Predictions must target the positive label **ICB responder** consistently. If an upstream model exports `P(non-responder)`, transform it to `1 - P(non-responder)` before assembly and record that transformation in the upstream model provenance. Do not guess a model's class order.

## Compare modalities fairly

The clinical model can use all available clinical patients for its development design; the planned mIF comparison includes the paired subset. To compare clinical, mIF, and fusion performance, use the same evaluation patients and splits for all three. Keep all slides or repeated measurements belonging to a patient in the same split. Fit preprocessing and fusion using only the appropriate training partition; evaluation predictions must remain held out or genuinely out of fold.

The planned 48 clinical patients and 29 with mIF are small cohorts. Report the paired sample size, number of responders, split method, uncertainty, and missing-modality handling alongside any metrics. Batch effects in extra mIF data need explicit handling by the modeling team before inclusion.

Useful model evaluation includes discrimination and calibration, along with threshold-dependent performance if a threshold was prespecified. A patient-level fused score that is higher than the clinical score is not evidence that fusion is more accurate. Claims of better clinical decisions or patient outcomes require additional evidence beyond this hackathon's narrative output. Transparent prediction-model reporting should follow the scope described in [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378).

The experiment's `metrics.json` computes exploratory AUROC, Brier score, and accuracy when eligible labels and supplied thresholds exist. It evaluates only records declared `test` or `out_of_fold` with a specified response definition, and keeps endpoint/partition groups separate. Use `paired_all_modalities` to compare all three models on the same patients; `available_cohorts` may contain different patients and is not the paired comparison. Labels are withheld from narrative generation. These metrics do not assess LLM correctness or certify calibration, split integrity, statistical significance, or clinical utility.

## Review the generated narratives

Use the four synthetic cases to inspect these behaviors before moving to real predictions:

| Case | Review focus |
| --- | --- |
| `P48` | All three scores are shown accurately and concordance is described without asserting treatment benefit. |
| `P12` | Clinical/mIF disagreement is visible; the fused score is not presented as resolving biological uncertainty. |
| `P07` | The narrative explicitly preserves absent mIF and fusion predictions. |
| `P29` | Scores near the supplied threshold are presented with appropriate caution; the threshold is not invented. |

Check the numbers against the structured prediction values. Check whether feature names, units, and context were reproduced accurately. Treat an elevated measurement as descriptive unless a signed, model-specific attribution was provided. An attribution concerns that model's prediction, not biological causation or treatment effect; attributions on different scales should not be compared directly.

Every narrative requires human review, including those with `quality.status = "passed"`. The implemented quality checks are limited automated safeguards, and a deterministic fallback is also a research summary. Junhao's UI should display predictions, modality availability, limitations, source, and review status so the basis of the summary is inspectable.

Do not use real patient results to test a hosted service. The inference workflow uses local weights; software/model download preparation can occur separately before real inputs are processed.
