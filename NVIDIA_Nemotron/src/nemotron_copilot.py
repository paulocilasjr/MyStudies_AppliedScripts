"""Public integration entry point; importing this module never loads a GPU model."""
from icb_copilot import Copilot, PatientPrediction, ContractError, generate_clinical_narrative

__all__ = ["Copilot", "PatientPrediction", "ContractError", "generate_clinical_narrative"]

if __name__ == "__main__":
    from icb_copilot.cli import main
    raise SystemExit(main())
