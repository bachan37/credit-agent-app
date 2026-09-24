import chromadb
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from credit_agent_app.config import settings

class SearchPastAssessmentsInput(BaseModel):
    query: str = Field(..., description="Query string or applicant name/PAN to search past loan evaluations.")

class VectorMemoryStore:
    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "loan_assessments"):
        # Connect to ChromaDB running inside Docker container
        self.chroma_client = chromadb.HttpClient(host=host, port=port)
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(api_key = settings.OPENAI_API_KEY),
        )

    def save_assessment(self, pan: str, name: str, assessment_summary: str, metadata: dict):
        print("Saving Assessment in vectorDB for {name}")
        doc = Document(
            page_content=f"Applicant: {name}, PAN: {pan}. Assessment Details: {assessment_summary}",
            metadata={"pan": pan, "name": name, **metadata}
        )
        self.vector_store.add_documents([doc], ids=[f"assessment_{pan}"])
    
    def search_similar(self, query: str, k: int = 3) -> str:
        """Searches vector store for relevant past assessment records."""
        docs = self.vector_store.similarity_search(query, k=k)
        if not docs:
            return "No matching past loan assessments found."
        return "\n".join([doc.page_content for doc in docs])

    def peek_chroma(self, limit: int = 10):
        """Debug helper to view ChromaDB content."""
        results = self.vector_store._collection.get(limit=limit)
        print("\n=================== CHROMADB CONTENTS ===================")
        print(f"Total items in collection: {self.vector_store._collection.count()}")
        for idx, (doc, meta, doc_id) in enumerate(zip(results["documents"], results["metadatas"], results["ids"])):
            print(f"\n--- Entry #{idx + 1} [ID: {doc_id}] ---")
            print(f"Metadata: {meta}")
            print(f"Document Text: {doc}")
        print("=========================================================\n")
    
# Initialize singleton vector store pointing to Docker
vector_memory_store = VectorMemoryStore(host="localhost", port=8000)

def _search_past_records(query: str) -> str:
    return vector_memory_store.search_similar(query)

# StructuredTool exposed to the Agent
search_past_assessments_tool = StructuredTool.from_function(
    func=_search_past_records,
    name="search_past_assessments",
    description="Searches long-term vector database for past applicant evaluations, previous credit decisions, and historical assessments.",
    args_schema=SearchPastAssessmentsInput
)
        