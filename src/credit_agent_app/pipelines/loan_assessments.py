from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from credit_agent_app.agents import credit_agent
from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional


class LoanAssessmentInput(BaseModel):
    name: str = Field(..., description="Name of the applicant")
    age: int = Field(..., description="Age of the applicant")
    pan: str = Field(..., description="PAN number of the applicant")
    salary_after_tax: float = Field(..., description="Monthly salary after tax")
    phone_number: str = Field(..., description="Phone number of the applicant")

class LoanAssessmentOutput(BaseModel):
    name: str = Field(..., description="Name of the applicant")
    age: int = Field(..., description="Age of the applicant")
    phone_number: str = Field(..., description="Phone number of the applicant")
    pan: str = Field(..., description="PAN number of the applicant")
    salary_after_tax: float = Field(..., description="Monthly salary after tax")
    credit_score: int = Field(..., description="Credit score of the applicant")
    monthly_obligation: float = Field(..., description="Monthly obligations of the applicant")
    eligible_loan_amount: float = Field(..., description="Eligible loan amount")
    max_emi: float = Field(..., description="Maximum monthly EMI")
    max_tenure: int = Field(..., description="Maximum loan tenure")
    status: Literal["Approved", "Rejected"] = Field(..., description="Status of the applicant's eligibility")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")

class LoanAssessmentPipeline:
    """LLM pipeline for loan assessment"""
    def __init__(self):
        self.agent = credit_agent
        self.parser = PydanticOutputParser(pydantic_object=LoanAssessmentOutput)
        self.prompt_template = ChatPromptTemplate(
            messages = [
                ("system", (
                    "You are a loan assessment agent.\n" 
                    "Your workflow: \n"
                    "1. Fetch credit details for the provided PAN using the `get_credit_details_by_pan` tool.\n"
                    "2. Calculate maximum loan eligibility using the `calculate_max_loan_eligibility` tool.\n"
                    "3. Determine the rate of interest using the `determine_rate_of_interest` tool.\n"
                    "4. Return the result in the specified instruction.\n"
                    "{format_instructions}"
                )),
                ("human", (
                    "Evaluate loan eligibility for the applicant:\n"
                    "- Name: {name}\n"
                    "- Age: {age}\n"
                    "- Phone: {phone_number}\n"
                    "- PAN: {pan}\n"
                    "- Monthly Salary After Tax: {salary_after_tax}"
                )),
            ],
            input_variables = ["name", "age", "phone_number", "pan", "salary_after_tax"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def run(self, input_data: Dict[str, Any] ):
        payload = LoanAssessmentInput(**input_data)
        print(payload)
        messages = self.prompt_template.format_messages(
            name=payload.name,
            age=payload.age,
            phone_number=payload.phone_number,
            pan=payload.pan,
            salary_after_tax=payload.salary_after_tax
        )
        
        agent_output = self.agent.invoke({"messages": messages})
        final_message_content = agent_output["messages"][-1].content
        return self.parser.parse(final_message_content)

