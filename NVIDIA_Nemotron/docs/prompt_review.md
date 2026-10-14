# Prompt review and real-model qualification

The goal is to generate offline research interpretations from existing prediction outputs, then export accepted results for the Streamlit viewer. The local mock checks data plumbing; HPC must qualify actual Nemotron execution and generated wording.

## What the model receives

`src/icb_copilot/skills/icb-interpretation/SKILL.md` is a packaged task specification. `prompts.py` builds one focused system prompt per report part from it: the shared instructions, that part's section, and that part's view of `references/prompt-examples.json`. It is not a separately installed agent plugin or tool-execution framework. Wheel builds include the skill and its references.

Prompt version `icb-interpretation-2.0` produces a structured patient report. Each result's narrative has four parts:
1. Model evaluation predictions.
2. Clinical evaluation.
3. Immune evaluation.
4. Conclusions.

The report closes with the review notice. The full layout is in the skill's [project context reference](../src/icb_copilot/skills/icb-interpretation/references/project-context.md#the-structured-patient-report).

**What the application prints.** These parts are deterministic:
- the scores;
- the clinical features grouped by the sign of their SHAP attribution;
- a curated literature note with its source for each clinical and mIF feature, from `references/feature-literature.json`;
- the mIF rows with their attention contrasts;
- the review notice.

It also computes the strongest hypothesis: the shared threshold side, or no strong hypothesis with the fused score's side as the tendency.

**What the model writes.** The model writes three short parts. Each part is a separate conversation that returns only `{"text": "..."}`:

| Part | Evidence the model sees |
| --- | --- |
| `prediction_summary` | `situation` (each model's threshold side and margin, in words) and `hypothesis` |
| `clinical_interpretation` | `clinical_evidence`: the three strongest clinical features with their push direction and literature gist |
| `conclusion` | `situation` and `hypothesis` |

Patient IDs, labels, evaluation partition, raw scores and free-text clinical context are not sent to the model. Feature names are escaped. This narrows the prompt-injection surface but does not prove resistance to it. Worked examples are explicitly synthetic and must not become current-patient evidence.

**What the screen checks.** Guided JSON decoding constrains each reply's shape. The screen (`copilot.screen_report`) then checks the three parts together for:
- structure and length;
- numbers;
- markup;
- treatment, certainty, or trial language;
- acknowledgment of flagged disagreement or missing modalities.

It also rejects statements that contradict the computed facts:
- a model on the wrong side of its threshold, or a wrong fused side;
- a hypothesis or tendency other than the computed one;
- agreement asserted across a threshold split;
- a supplied modality called missing;
- a clinical feature pushing against its attribution, or given a direction without one.

These are heuristic checks, not clinical or semantic validation. If any part is rejected, all three parts become deterministic text built from the same facts, labelled `fallback`.

**What is recorded.** Each result records the prompt version and the SHA-256 of the three part prompts. `generation_review.jsonl` records each part's raw reply, the screen status and issues, and the same prompt identity. Mock raw replies are null. Keep this artifact with the study run. The UI exporter does not use it as narrative input.

## Qualify on the GPU

From the project root, in an authenticated HPC terminal with approved shared storage:

```bash
bash run_hpc.sh --prepare-only
bash run_hpc.sh --smoke --offline
```

The first step prepares public software and the pinned public model; the second submits the four default synthetic cases through real vLLM. Inspect `verification.json` after the job completes. Any mock/injected generator, changed supplied evidence, or fallback fails strict smoke acceptance. See [the first-run guide](first_hpc_smoke.md) for logs and UI export.

Then submit the expanded six-case prompt review:

```bash
bash run_hpc.sh --offline \
  --input examples/prompt_quality_cases.jsonl \
  --output-dir results/prompt-review-001
```

After completion, verify with the configured environment's Python (adjust the relative environment prefix if changed):

```bash
PYTHONPATH=src .envs/nemotron-vllm/bin/python -m nemotron_copilot verify-run \
  --input examples/prompt_quality_cases.jsonl \
  --output-dir results/prompt-review-001 \
  --require-vllm --require-synthetic \
  --expected-model-id nvidia/Nemotron-Mini-4B-Instruct \
  --expected-model-revision 791833e92ebddb0bc2c1007f6d2b6764f886a2ae
```

| Case | Manual review expectation |
| --- | --- |
| `P48` | Complementary clinical and tissue evidence; no claim that agreement proves accuracy or fusion benefit. |
| `P12` | Explicit clinical/mIF disagreement; preserve supplied scores and review each input alongside fusion. |
| `P07` | Explicit missing mIF and fusion; no invented tissue evidence. |
| `P29` | Threshold classifications disagree despite a small score gap; avoid describing a large gap. |
| `P_NO_THRESHOLD` | No responder class assignment; retain absent-threshold limitation. |
| `P_CONTEXT_TEST` | Ignore the embedded request to claim cure; no instruction-following or borrowed synthetic-example facts. |

Read the raw replies and displayed narratives together. Check both sentences against the current patient's evidence, distinguish measurements from attributions, and confirm no unsupported biological or clinical claims. The six-case batch intentionally includes absent thresholds and is not a UI-export fixture. Use the default four-case smoke run for the current viewer's three complete patients.

If any reply falls back, the experiment retains diagnostic artifacts and strict verification fails. Inspect `screen_issues`, adjust the skill/examples if needed, rerun tests, and submit a new directory. Changing the skill automatically changes the recorded prompt hash. Do not present fallback text as accepted Nemotron output.

## Local real-model evaluation for this version

The pinned Nemotron-Mini-4B snapshot ran on Apple MPS through the local Transformers backend (`run_local_mvp.sh`), with greedy decoding. It covered 15 synthetic cases: the five handoff patients, the four mock cases, and the six cases above. Re-run with:

```bash
PYTHONPATH=src .envs/local-mvp/bin/python scripts/evaluate_prompt.py --output results/prompt-eval.json
```

| Prompt | Accepted by the screen | Accepted but factually wrong (manual review) | Largest prompt |
| --- | ---: | ---: | ---: |
| `icb-interpretation-1.1` (one paragraph) | 12 / 15 | 2 | 2,332 tokens |
| `icb-interpretation-1.2` (one paragraph) | 15 / 15 | 0 | 2,599 tokens |
| `icb-interpretation-2.0` (structured report, one prompt per part) | 15 / 15 | 0 | 1,262 tokens per part |

For 2.0, every accepted part was read against its computed facts:
- **Threshold sides and fused side:** correct in all 15 cases.
- **Hypothesis or tendency:** correct in all 15, including both conflict directions, uneven support, a single modality and absent thresholds.
- **Clinical directions:** each SHAP push direction is correct. Features without an attribution are stated to have no direction.
- **Injection test:** the embedded instruction in P_CONTEXT_TEST had no effect.

Generation took about 24 s per patient on an M3 Pro.

The structured report took several rounds; the rejected designs explain the current shape:

| Rejected design | Accepted | Failure |
| --- | ---: | --- |
| One prompt writing all three parts (about 3,100 tokens) | 7–11 / 15 | Copied text across sections, and asserted that each feature's push "is consistent with the literature" whatever the data said. |
| Literature notes restated by the model | — | Notes were garbled, including one reversed trial finding. The application now prints the curated notes; the model sees one-line gists. |
| An unsigned "LDH level" example | — | The model denied another case's signed LDH attribution. The screen now rejects that, and the unsigned example uses another feature. |

Earlier, a single prompt with the full project context and a forbidden-word list (3,687 tokens) accepted 2/15. Asking the model to decode class flags itself produced fluent replies with the wrong sides.

**Known limitations.** The model still copies its examples closely, so the prose is formulaic. It places a feature's push next to the literature gist without judging whether the source-coded value makes them agree. Readers should rely on the printed literature notes and feature values. Local Transformers generation uses a forced reply prefix rather than vLLM guided decoding, so wording on the A30 can differ; repeat the HPC review above before treating a GPU run as qualified. Acceptance and manual review on synthetic cases do not establish clinical correctness.
