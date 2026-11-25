https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


# E07: Normal tissue versus tumor exposure: matched-exposure run and budget sweep

Generated 2026-11-25T01:32:16+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

Tumor anchors per epoch by budget: X025: TCGA 2048, GTEx 4864, X050: TCGA 4096, GTEx 9728, X100: TCGA 8192, GTEx 19584, X200: TCGA 16384, GTEx 39168. Realized anchor presentations per run are in foundation_runs.tsv.

## LFT: families (cohort-and-patient intervals)

| family | checkpoints | estimate | bc_ci95_low | bc_ci95_high |
|---|---|---|---|---|
| A_U | 5 | 0.4123 | 0.2830 | 0.5254 |
| B_U | 5 | 0.4001 | 0.2959 | 0.4892 |
| C_U | 5 | 0.3996 | 0.2776 | 0.5056 |
| MIX_CEN_X025 | 3 | 0.3993 | 0.2796 | 0.5067 |
| MIX_CEN_X050 | 3 | 0.3864 | 0.2626 | 0.5008 |
| MIX_CEN_X100 | 3 | 0.3967 | 0.2729 | 0.5068 |
| MIX_CEN_X200 | 3 | 0.3909 | 0.2615 | 0.5170 |
| MIX_FED_X025 | 3 | 0.4280 | 0.3002 | 0.5293 |
| MIX_FED_X050 | 3 | 0.3859 | 0.2658 | 0.4946 |
| MIX_FED_X100 | 3 | 0.4289 | 0.3061 | 0.5407 |
| MIX_FED_X200 | 3 | 0.4028 | 0.2897 | 0.5042 |
| R | 1 | 0.4574 | 0.3158 | 0.5857 |
| TONLY_X025 | 3 | 0.4419 | 0.3167 | 0.5490 |
| TONLY_X050 | 3 | 0.4308 | 0.3074 | 0.5367 |
| TONLY_X100 | 5 | 0.4295 | 0.3031 | 0.5340 |
| TONLY_X200 | 3 | 0.4449 | 0.3099 | 0.5682 |

### Paired contrasts

| contrast | scope | estimate | q0025 | q0975 | paired_seeds | seed_mean | exact_sign_flip_p |
|---|---|---|---|---|---|---|---|
| normal_tissue_B_U_minus_T_MATCH | patient_within_fixed_cohorts | -0.0294 | -0.0678 | 0.0083 | 5 | -0.0294 | 0.3125 |
| normal_tissue_B_U_minus_T_MATCH | cohort_and_patient | -0.0294 | -0.0714 | 0.0159 | 5 | -0.0294 | 0.3125 |
| T_MATCH_minus_A_U | patient_within_fixed_cohorts | 0.0172 | -0.0103 | 0.0391 | 5 | 0.0172 | 0.1250 |
| T_MATCH_minus_A_U | cohort_and_patient | 0.0172 | -0.0202 | 0.0516 | 5 | 0.0172 | 0.1250 |
| normal_tissue_MIX_CEN_minus_TONLY_X025 | patient_within_fixed_cohorts | -0.0426 | -0.0839 | -0.0034 | 3 | -0.0426 | 0.2500 |
| normal_tissue_MIX_CEN_minus_TONLY_X025 | cohort_and_patient | -0.0426 | -0.0949 | 0.0106 | 3 | -0.0426 | 0.2500 |
| federation_MIX_FED_minus_MIX_CEN_X025 | patient_within_fixed_cohorts | 0.0288 | -0.0077 | 0.0673 | 3 | 0.0288 | 0.5000 |
| federation_MIX_FED_minus_MIX_CEN_X025 | cohort_and_patient | 0.0288 | -0.0416 | 0.0952 | 3 | 0.0288 | 0.5000 |
| normal_tissue_MIX_CEN_minus_TONLY_X050 | patient_within_fixed_cohorts | -0.0444 | -0.0805 | -0.0015 | 3 | -0.0444 | 0.2500 |
| normal_tissue_MIX_CEN_minus_TONLY_X050 | cohort_and_patient | -0.0444 | -0.0894 | 0.0030 | 3 | -0.0444 | 0.2500 |
| federation_MIX_FED_minus_MIX_CEN_X050 | patient_within_fixed_cohorts | -0.0005 | -0.0318 | 0.0276 | 3 | -0.0005 | 1.0000 |
| federation_MIX_FED_minus_MIX_CEN_X050 | cohort_and_patient | -0.0005 | -0.0381 | 0.0331 | 3 | -0.0005 | 1.0000 |
| normal_tissue_MIX_CEN_minus_TONLY_X100 | patient_within_fixed_cohorts | -0.0329 | -0.0631 | 0.0025 | 3 | -0.0427 | 0.5000 |
| normal_tissue_MIX_CEN_minus_TONLY_X100 | cohort_and_patient | -0.0329 | -0.0661 | 0.0064 | 3 | -0.0427 | 0.5000 |
| federation_MIX_FED_minus_MIX_CEN_X100 | patient_within_fixed_cohorts | 0.0323 | -0.0069 | 0.0658 | 3 | 0.0323 | 0.2500 |
| federation_MIX_FED_minus_MIX_CEN_X100 | cohort_and_patient | 0.0323 | -0.0194 | 0.0754 | 3 | 0.0323 | 0.2500 |
| normal_tissue_MIX_CEN_minus_TONLY_X200 | patient_within_fixed_cohorts | -0.0540 | -0.1176 | 0.0148 | 3 | -0.0540 | 0.2500 |
| normal_tissue_MIX_CEN_minus_TONLY_X200 | cohort_and_patient | -0.0540 | -0.1463 | 0.0267 | 3 | -0.0540 | 0.2500 |
| federation_MIX_FED_minus_MIX_CEN_X200 | patient_within_fixed_cohorts | 0.0119 | -0.0325 | 0.0491 | 3 | 0.0119 | 0.2500 |
| federation_MIX_FED_minus_MIX_CEN_X200 | cohort_and_patient | 0.0119 | -0.0470 | 0.0616 | 3 | 0.0119 | 0.2500 |

## Dose-response

| mode | strategy | scope | macro_AUPRC | slope_ci95_low | slope_ci95_high |
|---|---|---|---|---|---|
| LFT | TONLY | patient_within_fixed_cohorts | 0.0008 | -0.0096 | 0.0108 |
| LFT | TONLY | cohort_and_patient | 0.0008 | -0.0144 | 0.0159 |
| LFT | MIX_CEN | patient_within_fixed_cohorts | -0.0015 | -0.0143 | 0.0137 |
| LFT | MIX_CEN | cohort_and_patient | -0.0015 | -0.0259 | 0.0183 |
| LFT | MIX_FED | patient_within_fixed_cohorts | -0.0033 | -0.0188 | 0.0113 |
| LFT | MIX_FED | cohort_and_patient | -0.0033 | -0.0215 | 0.0136 |

Reading: normal tissue helps a cancer model only if MIX_CEN - TONLY is positive at matched tumor exposure. MIX - TONLY also adds compute (the GTEx anchors); TONLY at the next budget up is the equal-total-work comparison.
(END)
