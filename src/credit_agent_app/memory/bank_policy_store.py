## using this for knowledge base, upload pdfs and use them for answering queries
import os
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from credit_agent_app.config import settings
from typing import Optional

class BankPolicyStore:
    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "bank_policy_docs"):
        self.chroma_client = chromadb.HttpClient(host=host, port=port)
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
        )

    def search_policy(self, query: str, bank_name: Optional[str] = None, k: int = 4) -> str:
        """Retrieves top matching rules from ChromaDB with optional bank filtering."""
        filter_dict = {"bank_name": bank_name.lower()} if bank_name else None
        
        docs = self.vector_store.similarity_search(query, k=k, filter=filter_dict)
        if not docs:
            return f"No matching bank policy rules found{' for ' + bank_name if bank_name else ''}."
        
        results = []
        for d in docs:
            source_bank = d.metadata.get("bank_name", "general").upper()
            page = d.metadata.get("page", "N/A")
            results.append(f"[{source_bank} - Page {page}]: {d.page_content}")
            
        return "\n\n".join(results)

    def is_bank_ingested(self, bank_key: str) -> bool:
        """Checks if any documents exist in ChromaDB for the given bank key."""
        try:
            results = self.vector_store.get(where={"bank_name": bank_key.lower()})
            return len(results.get("ids", [])) > 0
        except Exception:
            return False

    def delete_bank_policy(self, bank_key: str):
        """Deletes all chunks corresponding to a specific bank."""
        print(f"Clearing existing vector records for bank: '{bank_key}'...")
        try:
            results = self.vector_store.get(where={"bank_name": bank_key.lower()})
            ids_to_delete = results.get("ids", [])
            if ids_to_delete:
                self.vector_store.delete(ids=ids_to_delete)
                print(f"Deleted {len(ids_to_delete)} existing chunks for '{bank_key}'.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def ingest_pdf(self, pdf_path: str, bank_key: str):
        """Loads a bank PDF, splits into chunks, and stores in ChromaDB."""
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file at '{pdf_path}' not found.")
            return

        print(f"Ingesting PDF: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        raw_docs = loader.load()

        # Split document into manageable semantic chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=[
                r"\n(?=\d+\.\s)",    # Matches any new line followed by numbers e.g. "\n1. ", "\n12. "
                r"\n(?=[A-Z\s]{4,}:)",# Matches capital section titles e.g. "\nELIGIBILITY:"
                "\n\n",             # Double newlines / paragraphs
                "\n• ",             # Bullet points
                "\n- ",             # Hyphenated lists
                "\n",               # Single newlines
                " "                 # Words
            ],
            chunk_size=800,
            chunk_overlap=120,
            is_separator_regex=True
        )

        chunks = text_splitter.split_documents(raw_docs)

        for chunk in chunks:
            chunk.metadata["bank_name"] = bank_key.lower()
            chunk.metadata["file_source"] = os.path.basename(pdf_path)

        # Index chunks in ChromaDB
        self.vector_store.add_documents(chunks)
        print(f"Successfully ingested {len(chunks)} policy chunks for '{bank_key.upper()}' into ChromaDB.")

bank_policy_store = BankPolicyStore()