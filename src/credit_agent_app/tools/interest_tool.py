from pydantic import BaseModel, Field   
from langchain_core.tools import tool

class InterestInput(BaseModel):
    credit_score: int = Field(..., 
    description="Credit score of the applicant. Should be between 300 and 900.",
    ge=300, le=900)

class InterestOutput(BaseModel):
    credit_score: int = Field(..., description="Credit score of the applicant")
    interest_rate: float = Field(..., description="Applicable annual interest rate percentage")

@tool("get_rate_of_interest", args_schema=InterestInput)
def get_rate_of_interest(credit_score: int) -> InterestOutput:
    """Takes a credit score and returns the applicable annual interest rate percentage."""
    print("get_rate_of_interest: Running")
    
    if credit_score >= 800:
        roi = 8.0
    elif credit_score >= 780:
        roi = 8.5
    elif credit_score >= 720:
        roi = 9.5
    elif credit_score >= 650:
        roi = 11.0
    else:   
        roi = 13.5

    print("get_rate_of_interest: returning result")
    return InterestOutput(credit_score=credit_score, interest_rate=roi)

    