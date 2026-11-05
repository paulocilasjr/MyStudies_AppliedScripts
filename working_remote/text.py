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





The path has a typo (HPC_reviwer_experiment). The correct one, after the usual sourcing:


bash HPC_reviewer_experiments/submit/E02_variance_decomposition.sh
bash HPC_reviewer_experiments/submit/E04_equivalence_tost.sh
Tab completion avoids this: type HPC_rev and press Tab.

Why only 5 run: the throttle allows 8, but the pending elements show reason Resources. The red partition has no free GPU slot that also has 8 free CPUs and 64 GB, so raising the throttle to 12 won't help by itself. Making each task smaller lets it fit into partly used GPU nodes; the pilot peaked at 2–4.5 GB of GPU memory, so 32 GB and 4 CPUs are plenty. Apply both changes to the elements still waiting:


scontrol update JobId=21663680 ArrayTaskThrottle=12 MinMemoryNode=32G NumCPUs=4    # rand-owners, pending part
scontrol update JobId=21663681 ArrayTaskThrottle=12 MinMemoryNode=32G NumCPUs=4    # rand-remaining
sinfo -p red -O NodeList:20,Gres:25,GresUsed:35,CPUsState,FreeMem,StateCompact     # free GPUs right now
If sinfo shows every GPU in use, you can't get more concurrency until GPUs free up.

Check elements 0 and 5. They are no longer in the queue. They may have finished, since the random encoder can stop early, or they may have failed. This matters: rand-remaining waits for every owner to succeed, so a single failed owner blocks the rest of the chain.


"$RX_PYTHON_TEST" HPC_reviewer_experiments/rx.py status E01
sacct -j 21663680 -X --format=JobID%16,State,Elapsed,ExitCode,NodeList
If both show COMPLETED, carry on. If either failed, paste the end of its log here before resubmitting:


tail -50 "$RX_ROOT/E01/logs/rand-owners.21663680_5.log"
