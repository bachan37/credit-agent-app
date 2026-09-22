from langchain_openai import ChatOpenAI
from credit_agent_app.config import settings


model = ChatOpenAI(model="gpt-5.6-luna", temperature=0, reasoning_effort="none", api_key=settings.OPENAI_API_KEY)
    
