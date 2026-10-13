# ICB copilot presentations

The current **32-slide deck** explains the application harness, future model handoffs, limitations, edge cases, trade-offs, and remaining decisions. Use the PowerPoint for presenting and editing; the PDF contains the same reviewed slides for convenient reading.

- [PowerPoint: architecture, execution, limitations and trade-offs](output/icb_copilot_limitations_tradeoffs_v2.pptx)
- [PDF: architecture, execution, limitations and trade-offs](output/icb_copilot_limitations_tradeoffs_v2.pdf)
- [Technical companion: commands, exact contracts, and input/output examples](../docs/copilot_execution_harness.md)
- [Original 12-slide architecture overview](output/icb_copilot_architecture_v2.pptx)
- [Previous 24-slide execution deck](output/icb_copilot_execution_harness_v3.pptx)

## Reading sequence

| Slides | Topic |
| --- | --- |
| 1–4 | Research scope, future prediction models, and the application harness around Nemotron. |
| 5–7 | HPC launch, selected runtime prerequisites, and token/execution budgets. |
| 8–11 | Patient joins, missing modalities, prediction/feature contracts, and prompt composition. |
| 12–16 | Output screening, expected result fields, synthetic example, recovery paths, and atomic publication. |
| 17–19 | Local API constraints, software tests, pending A30 checks, and proposed acceptance contracts. |
| 20–21 | Future model/UI handoffs and evaluation. |
| 22–25 | Cohort limitations, calibration/rounding, patient/evidence edge cases, and narrative-review limits. |
| 26–29 | Runtime/publication edge cases, deployment/modeling trade-offs, and proposed acceptance cases. |
| 30–32 | Proposed hardening, team decisions, and completion checkpoints. |

The deck distinguishes implemented checks from proposed additions. The responder definition remains unspecified. Existing software tests use mock/stub paths; actual Nemotron generation on Moffitt's A30 and independent clinical narrative review remain pending.

Text, tables, and charts are editable PowerPoint objects. Workflow illustrations are embedded images. Exact ImageGen prompts are recorded under `assets/image_prompts.md`, `assets/execution/image_prompts.md`, and `assets/contracts/image_prompts.md`. Sources and detailed execution qualifications are in the speaker notes and technical companion. The PDF uses reviewed slide renders and is intended as a visual preview.
