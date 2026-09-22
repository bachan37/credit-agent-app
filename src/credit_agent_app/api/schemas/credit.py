from pydantic import BaseModel, Field

class CreditResponse(BaseModel):
    pan: str = Field(..., description='PAN number of the applicant', min_length=10, max_length=10, pattern="^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    credit_score: int = Field(..., description='Credit score of the applicant')
    monthly_obligation: float = Field(..., description='Monthly obligation of the applicant')
