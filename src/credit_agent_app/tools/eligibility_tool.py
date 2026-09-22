from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class EligibilityInput(BaseModel):
    monthly_obligation: float = Field(..., description="Monthly obligation of the applicant. Should not be negative or zero.", ge=0)
    salary_after_tax: float = Field(..., description="Monthly salary of the applicant. Should not be negative or zero.", ge=0)
    age: int = Field(..., description="Age of the applicant. Should be between 18 and 60.", ge=18, le=60)
    rate_of_interest: float = Field(..., description="Annual interest rate percentage. Should not be negative or zero.", ge=0)

class EligibilityOutput(BaseModel): 
    eligible_loan_amount: float = Field(..., description="Maximum loan amount the applicant is eligible for")
    max_emi: float = Field(..., description="Maximum monthly EMI the applicant can afford")
    max_tenure: int = Field(..., description="Maximum loan tenure in years")
    status: str = Field(..., description="Status of the applicant's eligibility")

# function to calculate loan eligibility    
def calculate_loan_eligibility(monthly_obligation: float, salary_after_tax: float, age: int, rate_of_interest: float) -> EligibilityOutput:
    """Calculates maximum loan tenure, eligible loan amount, and resulting monthly EMI based on salary, obligation, and age."""
    print("calculate_loan_eligibility: Running")
    # Calculate max tenure (retirement at 60, capped at 30 years)
    max_tenure_years = min(30, max(1, 60 - age))

    # Max Obligation to income ration = 70% of monthly salary
    max_allowed_emi = (salary_after_tax * 0.70) - monthly_obligation

    # If max_allowed_emi is negative, return 0
    max_allowed_emi = max(0, max_allowed_emi)

    # Convert annual rate to monthly rate
    rate_monthly = (rate_of_interest / 100) / 12
    max_tenure_months = max_tenure_years * 12

    if max_allowed_emi == 0:
        print("calculate_loan_eligibility: max_allowed_emi is 0")
        return EligibilityOutput(
            eligible_loan_amount=0,
            max_emi=0,
            max_tenure=max_tenure_years,
            status="Ineligible for new loan due to high existing monthly obligations."
        )
    
    eligible_loan_amount = (max_allowed_emi * max_tenure_months) / (1 + rate_monthly * max_tenure_months)

    print("calculate_loan_eligibility: returning result")
    return EligibilityOutput(
        eligible_loan_amount=round(eligible_loan_amount, 2),
        max_emi=round(max_allowed_emi, 2),
        max_tenure=max_tenure_years,
        status="Eligible for new loan"
    )    

# structuredtool for the function
calculate_loan_eligibility_tool = StructuredTool.from_function(
    func=calculate_loan_eligibility,
    name="calculate_loan_eligibility",
    description="Calculates maximum loan tenure, eligible loan amount, and resulting monthly EMI based on salary, obligation, and age.",
    args_schema=EligibilityInput
)