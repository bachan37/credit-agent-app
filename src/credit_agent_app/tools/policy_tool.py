from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from credit_agent_app.memory.bank_policy_store import bank_policy_store

class SearchPolicyInput(BaseModel):
    query: str = Field(..., description="Query regarding bank policy rules, eligibility criteria, interest rates, prepayment fees, or charges.")
    bank_name: Optional[str] = Field(None, description="Optional bank identifier to filter terms (e.g., 'sbi', 'axis'). Leave blank if not specified by user.")

def _search_bank_terms(query: str, bank_name: Optional[str] = None) -> str:
    return bank_policy_store.search_policy(query=query, bank_name=bank_name)

search_bank_terms_tool = StructuredTool.from_function(
    func=_search_bank_terms,
    name="search_bank_terms",
    description="Use this tool when the user asks for specific rules, regulations, charges, fees, eligibility criteria, or interest rates related to a bank's loan policies. It provides precise policy snippets.",
    args_schema=SearchPolicyInput
)