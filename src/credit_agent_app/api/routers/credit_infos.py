from fastapi import APIRouter
from credit_agent_app.api.schemas import CreditResponse
from pydantic_core._pydantic_core import ValidationError

router = APIRouter(prefix="/credit-info", tags=["Credit Information"])

@router.get("/{pan}", response_model=CreditResponse)
def get_credit_info(pan: str):
    """GET /api/v1/credit-info/{pan} - Fetch credit metrics for a given PAN."""
    pan_upper = pan.upper()
    try:
        if pan_upper.startswith("ABC"):
            return CreditResponse(pan=pan_upper, credit_score=750, monthly_obligation=15000.0)
        elif pan_upper.startswith("CAAP"):
            return CreditResponse(pan=pan_upper, credit_score=800, monthly_obligation=5000.0)
        elif pan_upper.startswith("XYZ"):
            return CreditResponse(pan=pan_upper, credit_score=620, monthly_obligation=25000.0)
        else:
            return CreditResponse(pan=pan_upper, credit_score=700, monthly_obligation=10000.0)
    except ValidationError as e:
        return CreditResponse(pan="INVAL0000X", credit_score=0, monthly_obligation=0.0)
