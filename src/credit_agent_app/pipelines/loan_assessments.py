from langchain_core import chat_history
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import trim_messages
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from credit_agent_app.agents import credit_agent
from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional
from credit_agent_app.memory.vector_store import vector_memory_store
from credit_agent_app.memory.session_store import get_redis_chat_history, get_in_memory_history

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
    def __init__(self, use_redis: bool = False):
        self.agent = credit_agent
        self.parser = PydanticOutputParser(pydantic_object=LoanAssessmentOutput)
        self.vector_memory = vector_memory_store
        self.use_redis = use_redis

        # message trimmer
        self.trimmer = trim_messages(
            max_tokens=1000,
            strategy="last",
            token_counter=len,
            include_system=True,
            start_on="human",
        )

        self.prompt_template = ChatPromptTemplate(
            messages=[
                ("system", (
                    "You are an expert loan assessment agent.\n\n"
                    "Workflows & Routing Guidelines:\n"
                    "1. FOR QUESTIONS ABOUT BANK POLICY, TERMS, FEES, OR ELIGIBILITY RULES (e.g., SBI or Axis bank rules):\n"
                    "   - Call `search_bank_policy` to retrieve document facts.\n"
                    "   - Answer directly using natural, conversational text.\n"
                    "   - DO NOT format the response using the loan evaluation schema below.\n\n"
                    "2. FOR HISTORICAL OR GENERAL QUESTIONS ABOUT PAST APPLICANTS:\n"
                    "   - Call `search_past_assessments` to query ChromaDB.\n"
                    "   - Answer directly using natural text.\n\n"
                    "3. FOR NEW LOAN EVALUATIONS (when assessing a specific applicant/PAN):\n"
                    "   - Call `get_credit_details_by_pan`, `get_rate_of_interest`, and `calculate_loan_eligibility` sequentially.\n"
                    "   - ONLY FOR THIS WORKFLOW, format your final response strictly using the following schema instructions:\n"
                    "   {format_instructions}"
                )),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ],
            input_variables=["input"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    def run(self, input_text: str, session_id: str = "default_user", callbacks: Optional[list] = None) -> Any:
        history_factory = get_redis_chat_history if self.use_redis else get_in_memory_history
        history_store = history_factory(session_id)
        raw_history = history_store.messages
        
        # trim chat history
        trimmed_history = self.trimmer.invoke(raw_history)

        # Format the prompt template explicitly with trimmed history and input
        formatted_prompt = self.prompt_template.format_prompt(
            chat_history = trimmed_history,
            input = input_text,
        )

        agent_output = self.agent.invoke({"messages": formatted_prompt.to_messages()})

        final_message = agent_output["messages"][-1]
        final_content = final_message.content

        # Add to history
        history_store.add_user_message(input_text)
        history_store.add_ai_message(final_content)

        # Try parsing as structured output (for new loan evaluations)
        try:
            parsed_output = self.parser.parse(final_content)
            
            # Save completed assessment to ChromaDB vector store
            self.vector_memory.save_assessment(
                pan=parsed_output.pan,
                name=parsed_output.name,
                assessment_summary=(
                    f"Status: {parsed_output.status}, Credit Score: {parsed_output.credit_score}, "
                    f"Eligible Amount: {parsed_output.eligible_loan_amount}, Max EMI: {parsed_output.max_emi}, "
                    f"Tenure: {parsed_output.max_tenure} years, "
                    f"Phone Number: {parsed_output.phone_number}, "
                    f"Age: {parsed_output.age}, "
                    f"Name: {parsed_output.name}, "
                    f"PAN: {parsed_output.pan}, "
                    f"Monthly Obligation: {parsed_output.monthly_obligation}"
                ),
                metadata={
                    "status": parsed_output.status, 
                    "credit_score": parsed_output.credit_score, 
                    "name": parsed_output.name, 
                    "pan": parsed_output.pan,
                    "age": parsed_output.age
                }
            )
            return parsed_output
        except Exception:
            # Output was a conversational response or vector retrieval answer
            return final_content