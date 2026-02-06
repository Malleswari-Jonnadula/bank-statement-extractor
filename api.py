from fastapi import FastAPI, File, UploadFile
import pdfplumber
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)


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
def classify_with_llm(text, include_transactions=False):
    if include_transactions:
        prompt = f"""
        Extract only valid JSON from this bank statement text.
        Give account holder details,bank account details and transactions.
        Return keys: account_holder_details, bank_account_details, transactions.
        Text:
        {text}
        """
    else:
        prompt = f"""
        Extract only valid JSON from this bank statement text.
        Give account holder details related and bank account details related.
        Return keys: account_holder_details, bank_account_details.
        Text:
        {text}
        """

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

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
        result_json = classify_with_llm(text_content, include_transactions=False)
        transactions_csv = transactions_df.to_csv(index=False)
        return {
            "account_and_bank_details": result_json,
            "transactions": transactions_df.to_dict(orient="records"),
            "transactions_csv": transactions_csv
        }
    else:
        result_json = classify_with_llm(text_content, include_transactions=True)
        return {
            "all_details": result_json
        }
