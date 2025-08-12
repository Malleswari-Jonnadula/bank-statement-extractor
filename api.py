from fastapi import FastAPI, File, UploadFile
import pdfplumber
import pandas as pd
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()

# --- Pythonic extraction of transactions ---
def extract_transactions(pdf_file):
    all_rows = []
    columns = None

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            table = page.extract_table()
            if table:
                if columns is None:
                    columns = table[0]  # first row as header
                for row in table:
                    if row == columns:
                        continue
                    if any(skip in str(cell) for cell in row for skip in [
                        "Copyright", "Notes", "Bank Statement", "Dummy Bank Statement"
                    ]):
                        continue
                    all_rows.append(row)

    if columns and all_rows:
        df = pd.DataFrame(all_rows, columns=columns)
        return df
    return None

# --- Extract full text for Gemini ---
def extract_text(pdf_file):
    text_content = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    return text_content

# --- Gemini classification ---
def classify_with_gemini(text, include_transactions=False):
    if include_transactions:
        prompt = f"""
        You are given bank statement text.
        Extract:
        1. Account Holder Details: Name, Address, Contact Nr, Email
        2. Bank Account Details: Bank Name, Account Nr, IFSC Code, Bank Branch Address
        3. Tabular Data of Transactions
        Return in JSON format with keys: account_holder_details, bank_account_details, transactions.
        Text:
        {text}
        """
    else:
        prompt = f"""
        You are given bank statement text.
        Extract:
        1. Account Holder Details: Name, Address, Contact Nr, Email
        2. Bank Account Details: Bank Name, Account Nr, IFSC Code, Bank Branch Address
        Return in JSON format with keys: account_holder_details, bank_account_details.
        Text:
        {text}
        """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text

# --- Root endpoint ---
@app.get("/")
def read_root():
    return {"message": "Bank Statement Extraction API is running"}

# --- Upload PDF and Extract ---
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    transactions_df = extract_transactions(temp_path)
    text_content = extract_text(temp_path)

    if transactions_df is not None:
        result_json = classify_with_gemini(text_content, include_transactions=False)
        transactions_csv = transactions_df.to_csv(index=False)
        return {
            "account_and_bank_details": result_json,
            "transactions": transactions_df.to_dict(orient="records"),
            "transactions_csv": transactions_csv
        }
    else:
        result_json = classify_with_gemini(text_content, include_transactions=True)
        return {
            "all_details": result_json
        }
