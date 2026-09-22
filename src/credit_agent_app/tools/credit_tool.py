from langchain_core.tools import tool
from credit_agent_app.config import settings
import httpx
from pydantic import BaseModel, Field

class CreditInfoInput(BaseModel):
    pan: str = Field(..., 
        description="PAN number of the individual",
        min_length=10, max_length=10, pattern="^[A-Z]{5}[0-9]{4}[A-Z]{1}$")

class CreditInfoOutput(BaseModel):
    credit_score: int = Field(..., description="Credit score of the applicant", ge=0, le=900)
    monthly_obligation: float = Field(..., description="Monthly obligations of the applicant. Should not be negative", ge=0)

@tool("get_credit_details_by_pan", args_schema=CreditInfoInput)
def get_credit_details_by_pan(pan: str) -> CreditInfoOutput:   
    """Takes a PAN number and calls the static HTTP API to retrieve credit score and monthly obligations."""
    print("get_credit_details_by_pan: running")
    url = f"{settings.CREDIT_API_BASE_URL}/credit-info/{pan}"
    print(url)
    try:
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        print(f"get_credit_details_by_pan: {response.text}")
        return CreditInfoOutput(**response.json())
    except Exception as e:
        print(f"get_credit_details_by_pan Exception: {e}")
        return CreditInfoOutput(credit_score=0, monthly_obligation=0.0)