set -a; source hpc/site.env; set +a
for v in RX_PYTHON_TEST RX_PYTHON_FED RX_RESOURCES COMPASS_SOURCE FOUNDATION_DATASET CLINICAL_DATASET NEW_MODELS \
         CORE_LFT_PACKAGE CORE_PFT_PACKAGE PUBLISHED_REFERENCE CLINICAL_COST_REFERENCE; do
  [[ -e "${!v}" ]] && echo "ok       $v" || echo "MISSING  $v=${!v}"
done
ls "$CORE_ITERATION_ROOT/sample_objective/C_U_seed17.task.json"     # needed by E11
git check-ignore -q --no-index "$RX_ROOT" && echo "RX_ROOT is git-ignored"

srun --cpus-per-task=4 --mem=16G --time=00:45:00 ${CLINICAL_PARTITION:+--partition=$CLINICAL_PARTITION} \
  "$RX_PYTHON_TEST" -m unittest discover -s HPC_reviewer_experiments/tests -v


bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh --dry-run   # writes the plan, prints graph + sbatch
bash HPC_reviewer_experiments/submit/E05_per_cohort_auroc.sh             # one CPU job, no training


bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh --dry-run
bash HPC_reviewer_experiments/submit/E01_untrained_encoder.sh


for s in E02_variance_decomposition E03_seed_ensembling E04_equivalence_tost E10_biological_agreement E11_hpc_deployment; do
  bash HPC_reviewer_experiments/submit/$s.sh
done

for s in E06_federated_compass_recipe E07_tumor_exposure E08_client_partitions E08B_federated_algorithms E12_privacy_utility; do
  bash HPC_reviewer_experiments/submit/$s.sh --dry-run && bash HPC_reviewer_experiments/submit/$s.sh
done

conda activate compass-foundation-test
export TEST_CODE_DIR="$PWD/compass_hpc_foundation_model_test"
export TEST_PROJECT_ROOT=/share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test
export SYNAPSE_AUTH_TOKEN_FILE="$HOME/.config/synapse/compass_pat"
export COMPASS_RSCRIPT="$(conda run -n compass-data which Rscript)"
export PUBLIC_COHORT_SET=all16
export PUBLIC_RUN_TAG=public_all16_$(date -u +%Y%m%d_%H%M%SZ)
source "$TEST_CODE_DIR/config/settings.env"
bash "$TEST_CODE_DIR/scripts/submit_all_public_pipeline.sh"
echo "$PUBLIC_ITRP_PROCESSED_DIR"          # this becomes CLINICAL_DATASET_ALL16
conda deactivate


bash HPC_reviewer_experiments/submit/E13_broader_validation.sh --dry-run && bash HPC_reviewer_experiments/submit/E13_broader_validation.sh


bash HPC_reviewer_experiments/submit/E09_checkpoint_proxies.sh



set -a; source hpc/site.env; set +a
squeue -u "$USER"
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E06          # per-stage complete/failed/running
ls "$RX_ROOT/E06/logs/"                                              # one log per job / array element

# After fixing a failure, resubmit from the failed stage (finished work is reused)
bash HPC_reviewer_experiments/submit/E06_federated_compass_recipe.sh --from-stage recipe-owners

# Wrong path seen in a dry run, before any submit: fix hpc/site.env, then re-plan
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py plan E06 --force-new

# Export aggregate results into the repo (rechecked for patient-level content), review, then commit
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py export E06




less "$RX_ROOT/E05/results/report.md"                  # or: cat
ls "$RX_ROOT/E05/results/"
"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E05
column -t -s $'\t' "$RX_ROOT/E05/results/per_cohort_family.tsv" | less -S    # TSVs as aligned tables
This first real-data run also gives an end-to-end check. E05 rebuilds the family AUPRCs from the frozen core predictions, so they must equal the numbers you already reported. Print them:


awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next}
  $h["metric"]=="cohort_macro_AUPRC" && $h["scope"]=="cohort_and_patient" {printf "%-4s %s %.4f\n", $h["mode"], $h["family"], $h["estimate"]}' \
  "$RX_ROOT/E05/results/family_auprc_auroc.tsv"


(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ ls "$RX_ROOT/E05/results/"
cancer_type_summary.tsv  contrast_concentration.tsv  family_auprc_auroc.tsv  per_cohort_contrasts.tsv  per_cohort_family.tsv  report.md  results_receipt.json
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ "$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E05
analyze                      complete 1/1  failed 0  running 0
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ column -t -s $'\t' "$RX_ROOT/E05/results/per_cohort_family.tsv" | less -S
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ column -t -s $'\t' "$RX_ROOT/E05/results/per_cohort_family.tsv" | less -S
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next}
>   $h["metric"]=="cohort_macro_AUPRC" && $h["scope"]=="cohort_and_patient" {printf "%-4s %s %.4f\n", $h["mode"], $h["family"], $h["estimate"]}' \
>   "$RX_ROOT/E05/results/family_auprc_auroc.tsv"
LFT  A_U 0.4123
LFT  B_U 0.4001
LFT  C_U 0.3996
LFT  R 0.4574
PFT  A_U 0.4115
PFT  B_U 0.4008
PFT  C_U 0.4020
PFT  R 0.4434
(base) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
# E05: Per-cohort lift over responder rate, AUROC and concentration of gains

Generated 2026-11-05T21:51:37+00:00 from the frozen plan `plan.json`. Development evidence on exposed cohorts unless stated.

## LFT

| family | macro_AUPRC_lift_over_no_skill | macro_AUPRC_lift_over_rate | macro_AUROC | cohorts_AUROC_above_0.5 |
|---|---|---|---|---|
| A_U | 0.0437 | 0.0760 | 0.5606 | 8 |
| B_U | 0.0315 | 0.0639 | 0.5357 | 7 |
| C_U | 0.0311 | 0.0634 | 0.5344 | 6 |
| R | 0.0888 | 0.1211 | 0.5835 | 6 |

Concentration of family differences (AUPRC):

| contrast | macro_delta | cohorts_positive | cohorts | largest_positive_share | leave_one_cohort_out_min | leave_one_cohort_out_max |
|---|---|---|---|---|---|---|
| federation_C_U_minus_B_U | -0.0005 | 4 | 8 | 0.4759 | -0.0104 | 0.0092 |
| strategy_C_U_minus_A_U | -0.0126 | 2 | 8 | 0.8487 | -0.0281 | -0.0016 |
| gtex_B_U_minus_A_U | -0.0122 | 4 | 8 | 0.3239 | -0.0208 | 0.0009 |
| A_U_minus_R | -0.0451 | 3 | 8 | 0.4089 | -0.0621 | -0.0043 |
| B_U_minus_R | -0.0573 | 4 | 8 | 0.6955 | -0.0816 | -0.0220 |
| C_U_minus_R | -0.0577 | 3 | 8 | 0.5941 | -0.0764 | -0.0324 |

## PFT

| family | macro_AUPRC_lift_over_no_skill | macro_AUPRC_lift_over_rate | macro_AUROC | cohorts_AUROC_above_0.5 |
|---|---|---|---|---|
| A_U | 0.0429 | 0.0753 | 0.5617 | 7 |
| B_U | 0.0322 | 0.0646 | 0.5433 | 8 |
| C_U | 0.0334 | 0.0658 | 0.5401 | 6 |
| R | 0.0748 | 0.1072 | 0.5608 | 5 |

Concentration of family differences (AUPRC):

| contrast | macro_delta | cohorts_positive | cohorts | largest_positive_share | leave_one_cohort_out_min | leave_one_cohort_out_max |
|---|---|---|---|---|---|---|
| federation_C_U_minus_B_U | 0.0012 | 4 | 8 | 0.3401 | -0.0071 | 0.0139 |
| strategy_C_U_minus_A_U | -0.0095 | 5 | 8 | 0.5890 | -0.0200 | 0.0067 |
| gtex_B_U_minus_A_U | -0.0107 | 4 | 8 | 0.4234 | -0.0212 | 0.0060 |
| A_U_minus_R | -0.0319 | 5 | 8 | 0.3561 | -0.0458 | 0.0149 |
| B_U_minus_R | -0.0426 | 4 | 8 | 0.3011 | -0.0592 | 0.0010 |
| C_U_minus_R | -0.0414 | 5 | 8 | 0.3279 | -0.0563 | -0.0050 |

The no-skill AUPRC is the expected trapezoidal AUPRC of a random ranking for each cohort's size and prevalence; it exceeds the responder rate in small cohorts. Per-cohort intervals resample patients within that cohort only.
/share/lab_goecks/paulo/federated-learning-model/sources/raw/HPC_reviewer_experiments/run_20261105/E05/results/report.md (END)

family  mode  held_out_cohort  cancer_type  patients  responders  responder_rate       no_skill_AUPRC       AUPRC                AUPRC_ci95_low       AUPRC_ci95_high      AUPRC_lift_over_responder_rate  AUPRC>
A_U     LFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.24045991045991041  0.11771772349399097  0.3935814908029124   0.052959910459910414            -0.01>
A_U     LFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.6577271580058837   0.5913365290392846   0.7182575676365721   0.10978195252643164             0.097>
A_U     LFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.6697154958753883   0.5656911237716353   0.7621660165825644   0.13125395741384982             0.104>
A_U     LFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.28362306738831344  0.22337239571328693  0.35112902746323943  0.01695640072164678             -0.01>
A_U     LFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.263140213528348    0.18413673736482414  0.33655044662424527  0.06706178215579897             0.038>
A_U     LFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.23548404941701223  0.1766579599540871   0.3061441952161667   0.05570876851813583             0.036>
A_U     LFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.3579672702925688   0.2766520987065649   0.46156389747373955  0.024633936959235492            -0.01>
A_U     LFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.5899212337661138   0.4498645349971877   0.7299535355154321   0.14992123376611383             0.116>
B_U     LFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.28867806576139904  0.21950757575757576  0.45407965250158067  0.10117806576139904             0.035>
B_U     LFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.5935451640862436   0.5255206389154579   0.6628195291544859   0.04559995860679156             0.033>
B_U     LFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.614752365536938    0.5018913660217156   0.7178657256027594   0.07629082707539958             0.049>
B_U     LFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.31021314546287004  0.25670328361976724  0.3437805330628672   0.04354647879620338             0.015>
B_U     LFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.29791169358974984  0.19562300670147856  0.4089960844033039   0.10183326221720082             0.073>
B_U     LFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.2119048448093107   0.16786638352868005  0.273575872570034    0.03212956391043431             0.013>
B_U     LFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.3972542411026489   0.3228430356106727   0.47401035652169193  0.06392090776931558             0.019>
B_U     LFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.4864571957404958   0.41172629073826794  0.5748378362067516   0.04645719574049578             0.013>
C_U     LFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.22044273627606956  0.10069444444444443  0.37974547881679965  0.032942736276069556            -0.03>
C_U     LFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.6271832066746669   0.5593737942215683   0.6854482274824563   0.07923800119521485             0.066>
C_U     LFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.6439322352497459   0.4946164126551232   0.777532426635627    0.10547069678820742             0.078>
C_U     LFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.37932052802651006  0.3011801447323616   0.455344542013867    0.1126538613598434              0.084>
C_U     LFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.28020674526642675  0.18867573899731596  0.3773770910323269   0.08412831389387773             0.055>
C_U     LFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.18861134120778714  0.15744437147400264  0.22067483020178075  0.008836060308910737            -0.01>
C_U     LFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.35756412846085556  0.3064545606889665   0.44498690467201396  0.024230795127522242            -0.02>
C_U     LFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.499753374388863    0.3777419520842072   0.6308961048321682   0.05975337438886302             0.026>
R       LFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.27136412969746304  0.1223130819025958   0.4880952380952381   0.08386412969746304             0.018>
R       LFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.6246128046641921   0.5240311012938756   0.7245617193673072   0.07666759918474009             0.064>
R       LFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.596534618711296    0.43924300369559727  0.768252951035393    0.05807308024975755             0.030>
R       LFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.6143607558795532   0.4679551470998582   0.7443685806683841   0.3476940892128865              0.319>
R       LFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.2840552904475585   0.15642556203245056  0.50754968160969     0.08797685907500949             0.059>
R       LFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.26986714058044164  0.17742205819618778  0.3997697797387317   0.09009185968156525             0.071>
R       LFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.28442369535635786  0.21241934085203168  0.45018801161667604  -0.04890963797697545            -0.09>
R       LFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.7136736231431468   0.5127196088713266   0.8618201122534681   0.27367362314314675             0.240>
A_U     PFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.2504776242276242   0.09541666666666666  0.44755021755495444  0.06297762422762421             -0.00>
A_U     PFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.6314710535893752   0.5738791024866765   0.6795819267742134   0.08352584810992314             0.071>
A_U     PFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.6304419014489346   0.5363831431798746   0.7150993212073706   0.0919803629873962              0.064>
A_U     PFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.291466342559373    0.23020695988653042  0.34511049854015347  0.02479967589270632             -0.00>
A_U     PFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.27412712453590454  0.17989769490803656  0.36646105534634776  0.07804869316335553             0.049>
A_U     PFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.2412719886115541   0.18895063243663582  0.30207026977589113  0.061496707712677706            0.042>
A_U     PFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.35888313954379847  0.2744412934155342   0.4631015680297852   0.025549806210465154            -0.01>
A_U     PFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.6139254133032018   0.4801823768217582   0.7336164461005945   0.17392541330320183             0.140>
B_U     PFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.3130714193214193   0.2269175215242905   0.43597265678901387  0.1255714193214193              0.059>
B_U     PFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.5753733567329103   0.5206589777691741   0.63004862482687     0.02742815125345832             0.015>
B_U     PFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.6458978479316921   0.5225494739344972   0.7519917025791102   0.1074363094701537              0.080>
B_U     PFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.3030057122165045   0.25117260624056537  0.3402766525106545   0.036339045549837856            0.007>
B_U     PFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.24481617550844004  0.16862356976306367  0.32952720680514164  0.04873774413589102             0.020>
B_U     PFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.22119478305384543  0.1729722524383249   0.28508527700017855  0.041419502154969035            0.022>
B_U     PFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.4171160823549147   0.3468413416509916   0.4641317818577263   0.08378274902158139             0.039>
B_U     PFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.4856968093756631   0.39187227703921707  0.5896348001602794   0.04569680937566312             0.012>
C_U     PFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.2259031554864888   0.10150183150183151  0.38930682200413824  0.03840315548648879             -0.02>
C_U     PFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.634607032621694    0.5667537441514899   0.694559278671075    0.08666182714224202             0.074>
C_U     PFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.6359811995324729   0.5089211901563787   0.7604512766247467   0.09751966107093446             0.070>
C_U     PFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.3551967569459257   0.29513718732115213  0.40890701830869164  0.08853009027925901             0.060>
C_U     PFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.3022413420070381   0.19365906292006685  0.41687173335859495  0.1061629106344891              0.077>
C_U     PFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.20447328778384433  0.1615376105376246   0.25279347645890016  0.024698006884967927            0.005>
C_U     PFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.3665660969331911   0.3139841238600499   0.43654822126120096  0.03323276359985777             -0.01>
C_U     PFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.49101521710465473  0.3729915289141751   0.633580889360338    0.05101521710465473             0.017>
R       PFT   Choueiri         KIRC         16        3           0.1875               0.2533155084637584   0.26048149381482716  0.1149276254613894   0.4880952380952381   0.07298149381482716             0.007>
R       PFT   Gide             SKCM         73        40          0.547945205479452    0.5602167219256383   0.5932183848122938   0.5054151686771311   0.6887911712725633   0.045273179332841806            0.033>
R       PFT   Hugo             SKCM         26        14          0.5384615384615384   0.5656176280044957   0.5732870457471081   0.4210477127543378   0.7476765612112095   0.03482550728556966             0.007>
R       PFT   Kim              STAD         45        12          0.26666666666666666  0.2950658530504619   0.6510936917646113   0.5047749863852394   0.7982361301132908   0.38442702509794463             0.356>
R       PFT   Riaz             SKCM         51        10          0.19607843137254902  0.22428792062932276  0.2665613922417835   0.15009045539360275  0.4819266054794644   0.07048296086923447             0.042>
R       PFT   Rose             BLCA         89        16          0.1797752808988764   0.1988489285003393   0.17592418044770577  0.13459516823517095  0.2237846127732315   -0.003851100451170625           -0.02>
R       PFT   Snyder           BLCA         21        7           0.3333333333333333   0.3779480312522629   0.3436694188573888   0.24190633788683993  0.5153443708981728   0.01033608552405546             -0.03>
R       PFT   Zhao             GBM          25        11          0.44                 0.4732876104569174   0.682913888798414    0.4858212090712392   0.8467197421943383   0.24291388879841397             0.209>
(END)

