import sys
import uvicorn
from fastapi import FastAPI
from credit_agent_app.api.routers import api_v1_router
from credit_agent_app.pipelines import LoanAssessmentPipeline

app = FastAPI(title="Credit Agent Application")
app.include_router(api_v1_router)

@app.get("/")
def root():
    return {
        "message": "Credit Assessment API is running",
        "docs": "Visit /docs for Interactive API Documentation"
    }

def run_cli():
    print("===========================================")
    print("      Credit Assessment Agent CLI          ")
    print("===========================================\n")
    print("App loaded successfully! Enter details to begin.")
    # name = input("Applicant Name").strip() 
    # age = int(input("Age: ").strip())
    # phone = input("Phone Number").strip()
    # pan = input("PAN Number").strip()
    # salary = float(input("Monthly Salary After Tax").strip())
    name = "Bachan"
    age = 41
    phone = "9861245709"
    pan = "CAAPS1716B"
    salary = 80000

    input_data = {
        "name": name,
        "age": age,
        "phone_number": phone,
        "pan": pan,
        "salary_after_tax": salary,
    }

    print("executing pipeline")
    pipeline = LoanAssessmentPipeline()
    result = pipeline.run(input_data)
    print(result)
    

if __name__ == "__main__":
    # If 'server' argument is passed, launch FastAPI server with Uvicorn
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        uvicorn.run("credit_agent_app.main:app", host="127.0.0.1", port=8000, reload=True)
    else:
        # Default execution runs CLI
        run_cli()