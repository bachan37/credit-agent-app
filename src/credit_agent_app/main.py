import sys
import uuid
import uvicorn
from fastapi import FastAPI
from credit_agent_app.api.routers import api_v1_router
from credit_agent_app.pipelines import LoanAssessmentPipeline
from langchain_core.callbacks import StdOutCallbackHandler
from credit_agent_app.memory.session_store import inspect_redis_history

app = FastAPI(title="Credit Agent Application")
app.include_router(api_v1_router)

@app.get("/")
def root():
    return {
        "message": "Credit Assessment API is running",
        "docs": "Visit /docs for Interactive API Documentation"
    }

def run_cli():
    print("==================================================")
    print("      Credit Assessment Agent - Interactive CLI   ")
    print("==================================================")
    print("Type your query or assessment prompt below.")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    print(f"[Auto-generated Session ID: '{session_id}']")
    pipeline = LoanAssessmentPipeline(use_redis=True)
    print("-" * 50)

    while True:
        try:
            user_input = input("\nUser > ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nExiting session. Goodbye!")
                break

            # Debug command to inspect Redis
            if user_input.lower() == "/debug-redis":
                inspect_redis_history(session_id)
                continue

            # Debug command to inspect ChromaDB
            if user_input.lower() == "/debug-chroma":
                pipeline.vector_memory.peek_chroma()
                continue

            if not user_input:
                continue

            print("\n--- Agent Trace (Tools & Execution) ---")
            
            result = pipeline.run(
                input_text=user_input, 
                session_id=session_id,
                callbacks=[StdOutCallbackHandler()]
            )

            print("\n--- Final Agent Response ---")
            print(result)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nError processing request: {e}")
    
    

if __name__ == "__main__":
    # If 'server' argument is passed, launch FastAPI server with Uvicorn
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        uvicorn.run("credit_agent_app.main:app", host="127.0.0.1", port=8001, reload=True)
    else:
        # Default execution runs CLI
        run_cli()