import os
from credit_agent_app.memory.bank_policy_store import bank_policy_store

BANK_PDF_MAP = {
    "axis": "axis_loan_policy.pdf",
    "sbi": "sbi_loan_policy.pdf",
}

def process_ingestion(bank_key: str) -> None:
    pdf_name = BANK_PDF_MAP.get(bank_key)
    if not pdf_name:
        print(f"Error: Unknown bank key '{bank_key}'. Available keys: {list(BANK_PDF_MAP.keys())}")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(script_dir, "..", "docs", pdf_name)
    abs_pdf_path = os.path.normpath(relative_path)

    if not os.path.exists(abs_pdf_path):
        print(f"Error: PDF not found at '{abs_pdf_path}'")
        return

    # Check if bank is already imported
    if bank_policy_store.is_bank_ingested(bank_key):
        user_choice = input(
            f"Bank '{bank_key.upper()}' is already imported in ChromaDB.\n"
            f"Do you want to clean and re-ingest it? (y/n): "
        ).strip().lower()

        if user_choice in ["y", "yes"]:
            bank_policy_store.delete_bank_policy(bank_key)
            bank_policy_store.ingest_pdf(abs_pdf_path, bank_key)
        else:
            print("Skipped re-ingestion. Existing data retained.")
            return
    else:
        bank_policy_store.ingest_pdf(abs_pdf_path, bank_key)

def main():
    print("\nSelect a bank to ingest:")
    print("1. Axis Bank")
    print("2. SBI")
    choice = input("Enter choice (1-2): ").strip()
    bank_key = ""

    if choice == "1":
        bank_key = "axis"
    elif choice == "2":
        bank_key = "sbi"
    else:
        print("Invalid choice")
        return

    process_ingestion(bank_key)

if __name__ == "__main__":
    print("Script started...") 
    main()


    
