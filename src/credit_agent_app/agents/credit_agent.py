from langchain.agents import create_agent
from credit_agent_app.models import model
from credit_agent_app.tools import get_credit_details_by_pan_tool, calculate_loan_eligibility_tool, get_rate_of_interest_tool, search_past_assessments_tool, search_bank_terms_tool

# agent using model and tools
# Todo: dont like var name "model", rename it.
credit_agent = create_agent(
    model=model, 
    # Todo: the tool list may get longer, need to find better way.
    tools=[
        get_credit_details_by_pan_tool, 
        calculate_loan_eligibility_tool, 
        get_rate_of_interest_tool,
        search_past_assessments_tool,
        search_bank_terms_tool
    ]
)

