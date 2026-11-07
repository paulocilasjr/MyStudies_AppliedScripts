Benchmark Reruns and Accuracy Changes 

October 28 2026 

This report compares the original benchmark results with 77 reruns: 55 in CompBioBench (28 Galaxy and 27 Open-ended code), 19 in BixBench (16 Galaxy and three Open-ended code), and three in the IWC workflow benchmark (one Galaxy and two Open-ended code). It summarizes the resulting accuracy changes and provides links to the analysis records. 

Galaxy runs use tools on the Galaxy analysis platform. Open-ended code runs execute analysis code outside Galaxy. R1, R2 and R3 identify the three experimental replicates. Accuracy is reported separately for each benchmark because the scoring metrics differ. 

CompBioBench official accuracy by replicate 

Before and After are the official leaderboard scores before and after rerunning the listed questions in each 100-answer submission. Change is measured in percentage points.  

Galaxy replicates 

Model 

Replicate 

Rerun questions 

Changed answers 

Before 

After 

Change 

GPT-5.5 

R3 

1 

0 

86% 

86% 

0 

DeepSeek-v4-pro-0813 

R1 

5 

3 

85% 

86% 

+1 

DeepSeek-v4-pro-0813 

R2 

6 

4 

86% 

85% 

-1 

DeepSeek-v4-pro-0813 

R3 

9 

5 

83% 

85% 

+2 

GPT-5.6 Luna Max 

R1 

5 

1 

87% 

86% 

-1 

GPT-5.6 Luna Max 

R2 

1 

1 

84% 

83% 

-1 

GPT-5.6 Luna Max 

R3 

1 

0 

85% 

85% 

0 

 

Open-ended code replicates 

Model 

Replicate 

Rerun questions 

Changed answers 

Before 

After 

Change 

GPT-5.6 Sol 

R1 

1 

0 

88% 

88% 

0 

GPT-5.6 Sol 

R2 

1 

0 

90% 

90% 

0 

DeepSeek-v4-pro-0813 

R1 

3 

1 

80% 

81% 

+1 

DeepSeek-v4-pro-0813 

R2 

8 

2 

87% 

86% 

-1 

DeepSeek-v4-pro-0813 

R3 

6 

3 

86% 

88% 

+2 

GPT-5.6 Luna Max 

R1 

4 

0 

85% 

85% 

0 

GPT-5.6 Luna Max 

R2 

3 

1 

86% 

85% 

-1 

GPT-5.6 Luna Max 

R3 

1 

1 

85% 

84% 

-1 

 

CompBioBench mean accuracy across replicates 

DeepSeek-v4-pro-0813 increased from 84.33% to 85.00% in Open-ended code and from 84.67% to 85.33% in Galaxy. GPT-5.6 Luna Max decreased from 85.33% to 84.67% in both conditions. GPT-5.5 and GPT-5.6 Sol retained their previous official scores. 

Across the four paired CompBioBench models, mean official accuracy is 87.00% for Galaxy and 86.75% for Open-ended code, a difference of 0.25 percentage points. These overall means are unchanged from the previous published results. 

CompBioBench reruns by question 

The tables compare the original and rerun answers for 55 CompBioBench runs; 22 answer strings changed. Each row links to the Galaxy history (analysis jobs and datasets), where applicable, the execution trace (tool calls and outputs), and the benchmark question page.  

GPT-5.5 Galaxy R3 

1 rerun question; 0 changed answers; official accuracy 86% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

lung-cancer-sc-q1 

Read the public same-question results page and another agent's Galaxy history, including analysis scripts and results. 

Unchanged 

Patient_018;40 

1) History 

2) Trace 

3) Question page 

 

GPT-5.6 Sol Open-ended code R1 

1 rerun question; 0 changed answers; official accuracy 88% to 88%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

covid-patient-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

1,5,11,12,17,21,24,27,29,32 

1) Trace 

2) Question page 

 

GPT-5.6 Sol Open-ended code R2 

1 rerun question; 0 changed answers; official accuracy 90% to 90%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

differential-composition-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

horizontal cell 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Galaxy R1 

5 rerun questions; 3 changed answers; official accuracy 85% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

afgr-1000g-intersect-atac-q1 

The sample intersection compared names directly and missed individuals recorded with GM versus NA aliases. 

Original: 50,054938323525a222bcc6154a05996ace 

Rerun: 83,1127bd47e06e7c19e8f0d5b5458a244a 

1) History 

2) Trace 

3) Question page 

cell-proportions-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

50;35;15 

1) History 

2) Trace 

3) Question page 

compute-gccontent-promoter-q1 

Promoter expansion ignored the negative transcript strand, so GC content was calculated for the wrong interval. 

Original: 17;7686990;7687589;-;600;331;0.55 

Rerun: 17;7687391;7687990;-;600;292;0.49 

1) History 

2) Trace 

3) Question page 

contaminated-rna-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

sus scrofa 

1) History 

2) Trace 

3) Question page 

covid-patient-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: 1,5,11,12,17,21,24,27,29,32 

Rerun: 1,2,4,5,6,7,8,9,10,11,12,15,16,17,19,20,21,22,23,24,25,27,28,29,32 

1) History 

2) Trace 

3) Question page 

 

DeepSeek-v4-pro-0813 Galaxy R2 

6 rerun questions; 4 changed answers; official accuracy 86% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

afgr-1000g-intersect-atac-q1 

The sample intersection compared names directly and missed individuals recorded with GM versus NA aliases. 

Original: 50,054938323525a222bcc6154a05996ace 

Rerun: 83,1127bd47e06e7c19e8f0d5b5458a244a 

1) History 

2) Trace 

3) Question page 

atac-doublet-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

AACATGGAGCGCCGGG-1 

1) History 

2) Trace 

3) Question page 

covid-patient-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: 1,5,11,12,17,21,24,27,29,32 

Rerun: 1,5,6,8,10,11,12,15,17,19,21,22,23,24,25,27,29,32 

1) History 

2) Trace 

3) Question page 

histone-chip-q1 

Read an earlier execution log or excerpt for the same question. 

Original: H3K9me3 

Rerun: H3K27ac 

1) History 

2) Trace 

3) Question page 

reverse-encode-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

ENCSR597URK 

1) History 

2) Trace 

3) Question page 

reverse-search-gwas-q1 

Read a commit diff of a public execution trace for the same question, including its answer. 

Original: 28628107 

Rerun: 33303764 

1) History 

2) Trace 

3) Question page 

 

DeepSeek-v4-pro-0813 Galaxy R3 

9 rerun questions; 5 changed answers; official accuracy 83% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

1000G-retrieve-genotype-q1 

Read a public summary of an earlier execution trace for the same question. 

Original: 0|1,1|0,1|1,1|1,0|1,1|1,0|0,1|0,0|1,1|1 

Rerun: 0/1,1/0,1/1,1/1,0/1,1/1,0/0,1/0,0/1,1/1 

1) History 

2) Trace 

3) Question page 

1000G-retrieve-genotype-q2 

Read an earlier same-question results JSON containing the answer. 

Unchanged 

296;864b06501a76b44b3037072e25c99725 

1) History 

2) Trace 

3) Question page 

atac-doublet-q1 

Read earlier same-question results. A first independent rerun returned no doublet, prompting a second analysis using fragment-overlap evidence. 

Unchanged 

AACATGGAGCGCCGGG-1 

1) History 

2) Trace 

3) Question page 

cell-proportions-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

50;35;15 

1) History 

2) Trace 

3) Question page 

exogenous-mix-reads-q1 

Repeated the mixture estimate with independent alignments and an explicit assessment of reads not explained by the endogenous references. 

Original: 50 

Rerun: 30 

1) History 

2) Trace 

3) Question page 

gtf-5-utr-median-len-q1 

Exon overlaps were aggregated without requiring matching transcript IDs, mixing coding or untranslated segments from different transcripts. 

Original: 133;1302;1056 

Rerun: 133;1296;1050 

1) History 

2) Trace 

3) Question page 

 

DeepSeek-v4-pro-0813 Galaxy R3 continued 

9 rerun questions; 5 changed answers; official accuracy 83% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

gwas-ancestry-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: HIS 

Rerun: AFR 

1) History 

2) Trace 

3) Question page 

lung-cancer-sc-q1 

Repeated the marker-based cell classification and patient-specific counting to check the reported malignant-cell proportion. 

Original: Patient_018;20 

Rerun: Patient_018;40 

1) History 

2) Trace 

3) Question page 

reverse-encode-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

ENCSR597URK 

1) History 

2) Trace 

3) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R1 

3 rerun questions; 1 changed answer; official accuracy 80% to 81%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

gwas-ancestry-q1 

Read an earlier execution log or excerpt for the same question. 

Original: AFR 

Rerun: HIS 

1) Trace 

2) Question page 

perturb-seq-align-q1 

Read an earlier execution log or excerpt for the same question. 

Unchanged 

guide18,guide13,guide14 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R1 continued 

3 rerun questions; 1 changed answer; official accuracy 80% to 81%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

spatial-sim-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

Fibroblast_Stroma,Macrophage 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R2 

8 rerun questions; 2 changed answers; official accuracy 87% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

borzoi-basic-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

190902667 

1) Trace 

2) Question page 

compute-gccontent-promoter-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

17;7687391;7687990;-;600;292;0.49 

1) Trace 

2) Question page 

contaminated-rna-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: rattus norvegicus 

Rerun: lymphocryptovirus humangamma4 

1) Trace 

2) Question page 

covid-patient-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

1,5,11,12,17,21,24,27,29,32 

1) Trace 

2) Question page 

exogenous-mix-reads-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

NA 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R2 continued 

8 rerun questions; 2 changed answers; official accuracy 87% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

gwas-ancestry-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

HIS 

1) Trace 

2) Question page 

reverse-search-gwas-q1 

Read an earlier execution log or excerpt for the same question. 

Original: 41491094 

Rerun: 40593539 

1) Trace 

2) Question page 

three-way-barnyard-q1 

Downloaded and read an earlier execution log for the same question, including its prior results. 

Unchanged 

10;30;60 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R3 

6 rerun questions; 3 changed answers; official accuracy 86% to 88%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

1000G-retrieve-genotype-q1 

Read a public summary of an earlier execution trace for the same question. 

Original: 0|1,1|0,1|1,1|1,0|1,1|1,0|0,1|0,0|1,1|1 

Rerun: 0/1,0/1,1/1,1/1,0/1,1/1,0/0,0/1,0/1,1/1 

1) Trace 

2) Question page 

contaminated-rna-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: rattus norvegicus 

Rerun: sus scrofa 

1) Trace 

2) Question page 

gwas-ancestry-q1 

Read an earlier execution log or excerpt for the same question. 

Unchanged 

HIS 

1) Trace 

2) Question page 

 

DeepSeek-v4-pro-0813 Open-ended code R3 continued 

6 rerun questions; 3 changed answers; official accuracy 86% to 88%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

hic-differential-loop-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

7720000;7800000 

1) Trace 

2) Question page 

perturb-seq-align-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

guide18,guide13,guide14 

1) Trace 

2) Question page 

reverse-search-gwas-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: 28628107 

Rerun: 33710309 

1) Trace 

2) Question page 

 

GPT-5.6 Luna Max Galaxy R1 

5 rerun questions; 1 changed answer; official accuracy 87% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

atac-tn5-shift-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

2;-1 

1) History 

2) Trace 

3) Question page 

borzoi-rnaseq-q1 

Read the contents of another run's Galaxy history for the same question. 

Unchanged 

9380 

1) History 

2) Trace 

3) Question page 

 

GPT-5.6 Luna Max Galaxy R1 continued 

5 rerun questions; 1 changed answer; official accuracy 87% to 86%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

encode-atac-pipeline-q1 

Read the contents of another run's Galaxy history for the same question. 

Unchanged 

13636 

1) History 

2) Trace 

3) Question page 

reverse-search-gwas-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: 41491094 

Rerun: 32929287 

1) History 

2) Trace 

3) Question page 

splice-pred-q1 

Read the contents of another run's Galaxy history for the same question. 

Unchanged 

7 

1) History 

2) Trace 

3) Question page 

 

GPT-5.6 Luna Max Galaxy R2 

1 rerun question; 1 changed answer; official accuracy 84% to 83%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

tissue-fibroblast-q1 

Read the public same-question results page, which included earlier answers. 

Original: Lung,Bone 

Rerun: Lung,Lymph node 

1) History 

2) Trace 

3) Question page 

 

GPT-5.6 Luna Max Galaxy R3 

1 rerun question; 0 changed answers; official accuracy 85% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

saluki-setup-optimize-q1 

Read the contents of another run's Galaxy history for the same question. 

Unchanged 

GCCGCCACCATGGTGAGCAAGGGCGAGTAGTATAAATAATAAGGGCT 

1) History 

2) Trace 

3) Question page 

 

GPT-5.6 Luna Max Open-ended code R1 

4 rerun questions; 0 changed answers; official accuracy 85% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

conservation-lookup-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

0,7,0,20,5,24,27 

1) Trace 

2) Question page 

covid-patient-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

1,5,11,12,17,21,24,27,29,32 

1) Trace 

2) Question page 

gwas-ancestry-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

HIS 

1) Trace 

2) Question page 

reverse-search-gwas-q2 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

36224396 

1) Trace 

2) Question page 

 

GPT-5.6 Luna Max Open-ended code R2 

3 rerun questions; 1 changed answer; official accuracy 86% to 85%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

differential-composition-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: horizontal cell 

Rerun: rod cell 

1) Trace 

2) Question page 

finding-geo-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

GSE114176 

1) Trace 

2) Question page 

mystery-peak-set-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Unchanged 

S5 

1) Trace 

2) Question page 

 

GPT-5.6 Luna Max Open-ended code R3 

1 rerun question; 1 changed answer; official accuracy 85% to 84%. 

Question 

Reason for rerun 

Original and new answers 

Rerun links 

conservation-lookup-q1 

Read a previous answer or the execution trace of an earlier run for the same question. 

Original: 0,7,0,20,5,24,27 

Rerun: 9,16,9,29,14,24,35 

1) Trace 

2) Question page 

 

BixBench rerun results 

The BixBench reruns comprise 19 DeepSeek V4 Pro runs: 16 Galaxy and three Open-ended code. Fourteen original runs accessed answers or agent traces for the same question, including three direct-copy runs for bix-30-q3. The other five retrieved answer-related material without confirmed exposure to their own question's answer. 

Accuracy is the number of correct answers out of 150 per model and condition (50 questions with three replicates). Before shows the published accuracy before the reruns and the ground truth update described below. The GPT-5.5 changes reflect re-evaluation under the updated ground truth, not new model runs. 

Model 

Condition 

Reruns 

Baseline 

Before 

After 

Change pp 

GPT-5.5 

Galaxy 

0 

137/150 

91.33% 

93.33% 

+2.00 

GPT-5.5 

Open-ended code 

0 

135/150 

90.00% 

92.00% 

+2.00 

GPT-5.6 Sol 

Galaxy 

0 

136/150 

90.67% 

92.67% 

+2.00 

GPT-5.6 Sol 

Open-ended code 

0 

134/150 

89.33% 

89.33% 

+0.00 

GPT-5.6 Luna 

Galaxy 

0 

130/150 

86.67% 

88.67% 

+2.00 

GPT-5.6 Luna 

Open-ended code 

0 

133/150 

88.67% 

89.33% 

+0.67 

DeepSeek V4 Pro 

Galaxy 

16 

126/150 

84.00% 

83.33% 

-0.67 

DeepSeek V4 Pro 

Open-ended code 

3 

124/150 

82.67% 

82.67% 

+0.00 

 

For bix-45-q1, the reference answer accepts both 7.6968e-54 and the independently reproduced newer-version result 1.5197572608715265e-56, with 5% relative tolerance around each. This rule applies to every model and condition. The DeepSeek Galaxy reruns reduced the number of correct answers by four; the ground truth update added three passes, changing the total from 126 to 125 out of 150. Open-ended code remained at 124 out of 150. 

BixBench reruns by question 

Run 

Reason for rerun 

Original and rerun answer 

Links 

bix-11-q2 
Galaxy R1 

The earlier run read same-question answers or another agent's execution trace. 

Original: 35% 
PASS 

Rerun: 35.341365461847% 
PASS 

1) History 

2) Trace 

3) Question page 

bix-26-q5 
Galaxy R1 

The earlier run read same-question answers or another agent's execution trace. 

Original:  
FAIL 

Rerun: 1 
FAIL 

1) History 

2) Trace 

3) Question page 

bix-30-q3 
Galaxy R1 

The earlier run directly copied a published answer for this question. 

Original: 0:0 
PASS 

Rerun: 1:0 
FAIL 

1) History 

2) Trace 

3) Question page 

bix-51-q8 
Galaxy R1 

The earlier run read same-question answers or another agent's execution trace. 

Original: -0.0749537657284774 
PASS 

Rerun: -0.07495391804 
PASS 

1) History 

2) Trace 

3) Question page 

bix-52-q2 
Galaxy R1 

Retrieved answer-related material; exposure to this question's own answer was not confirmed. 

Original: 1.12826e-07 
PASS 

Rerun: 1.1282568023118e-07 
PASS 

1) History 

2) Trace 

3) Question page 

 

BixBench reruns by question continued 

Run 

Reason for rerun 

Original and rerun answer 

Links 

bix-54-q7 
Galaxy R1 

Retrieved answer-related material; exposure to this question's own answer was not confirmed. 

Original: 184371.846023061 
PASS 

Rerun: 180771.363486404 
FAIL 

1) History 

2) Trace 

3) Question page 

bix-11-q1 
Galaxy R2 

The earlier run read same-question answers or another agent's execution trace. 

Original: 0.05 
PASS 

Rerun: 0.0501 
PASS 

1) History 

2) Trace 

3) Question page 

bix-18-q3 
Galaxy R2 

Retrieved answer-related material; exposure to this question's own answer was not confirmed. 

Original: 70.98577995932499% 
PASS 

Rerun: 71% 
PASS 

1) History 

2) Trace 

3) Question page 

bix-30-q3 
Galaxy R2 

The earlier run directly copied a published answer for this question. 

Unchanged 

0:0 
PASS 

1) History 

2) Trace 

3) Question page 

bix-38-q1 
Galaxy R2 

The earlier run read same-question answers or another agent's execution trace. 

Original: 2.1775 
PASS 

Rerun: 2.177508967 
PASS 

1) History 

2) Trace 

3) Question page 

 

BixBench reruns by question continued 

Run 

Reason for rerun 

Original and rerun answer 

Links 

bix-43-q4 
Galaxy R2 

The earlier run read same-question answers or another agent's execution trace. 

Unchanged 

8/49 
PASS 

1) History 

2) Trace 

3) Question page 

bix-16-q3 
Galaxy R3 

Retrieved answer-related material; exposure to this question's own answer was not confirmed. 

Unchanged 

3 
PASS 

1) History 

2) Trace 

3) Question page 

bix-26-q5 
Galaxy R3 

The earlier run read same-question answers or another agent's execution trace. 

Original: 3 
PASS 

Rerun: 1 
FAIL 

1) History 

2) Trace 

3) Question page 

bix-30-q3 
Galaxy R3 

The earlier run directly copied a published answer for this question. 

Original: 0:0 
PASS 

Rerun: 1:0 
FAIL 

1) History 

2) Trace 

3) Question page 

bix-38-q1 
Galaxy R3 

The earlier run read same-question answers or another agent's execution trace. 

Original: 2.1775 
PASS 

Rerun: 2.17750896687531 
PASS 

1) History 

2) Trace 

3) Question page 

 

BixBench reruns by question continued 

Run 

Reason for rerun 

Original and rerun answer 

Links 

bix-46-q4 
Galaxy R3 

The earlier run read same-question answers or another agent's execution trace. 

Unchanged 

-4.10 
PASS 

1) History 

2) Trace 

3) Question page 

bix-12-q6 
Open-ended code R1 

The earlier run read same-question answers or another agent's execution trace. 

Unchanged 

6748.0 
PASS 

1) Trace 

2) Question page 

bix-26-q5 
Open-ended code R3 

Retrieved answer-related material; exposure to this question's own answer was not confirmed. 

Unchanged 

1 
FAIL 

1) Trace 

2) Question page 

bix-32-q2 
Open-ended code R3 

The earlier run read same-question answers or another agent's execution trace. 

Unchanged 

2 
FAIL 

1) Trace 

2) Question page 

 

IWC rerun results 

Three DeepSeek V4 Pro runs were repeated for the IWC peptide-to-protein verification task (wf_009_clinicalmp_peptide_verification): Galaxy R2 and Open-ended code R1 and R2.  

 

Model 

Condition 

Reruns 

Baseline 

Before 

After 

Change pp 

DeepSeek V4 Pro 

Galaxy 

1 

30 runs 

99.94% 

99.88% 

-0.06 

DeepSeek V4 Pro 

Open-ended code 

2 

30 runs 

96.28% 

95.92% 

-0.36 

 

The run-level table gives peptide-protein F1 scores. Full submitted tables and evaluations are available through the execution traces and question pages. 

IWC peptide verification reruns 

Run 

Reason for rerun 

Peptide protein F1 

Links 

wf_009 
Galaxy R2 

The earlier run read expected peptide-protein matches or their UniProt outputs. 

Original: Peptide-protein F1 
100.00% 

Rerun: Peptide-protein F1 
98.23% 

1) History 

2) Trace 

3) Question page 

wf_009 
Open-ended code R1 

The earlier run read expected peptide-protein matches or their UniProt outputs. 

Original: Peptide-protein F1 
100.00% 

Rerun: Peptide-protein F1 
98.23% 

1) Trace 

2) Question page 

wf_009 
Open-ended code R2 

The earlier run read expected peptide-protein matches or their UniProt outputs. 

Original: Peptide-protein F1 
99.28% 

Rerun: Peptide-protein F1 
90.26% 

1) Trace 

2) Question page 

 

Benchmark results and analysis records 

The links below provide machine-readable results for each benchmark. The data index lists the JSON downloads, and the question pages link to individual runs and their analysis records. 

All benchmark data 

CompBioBench results 

BixBench results 

IWC results 
