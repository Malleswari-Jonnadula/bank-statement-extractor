import streamlit as st
import pdfplumber
import pandas as pd
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()


GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
# --- Pythonic extraction of transactions ---
def extract_transactions(pdf_file):
    all_rows = []
    columns = None

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            table = page.extract_table()
            if table:
                if columns is None:
                    # Take column headers only from first page
                    columns = table[0]
                for row in table:
                    # Skip header rows from later pages
                    if row == columns:
                        continue
                    # Skip junk/footer rows
                    if any(skip in str(cell) for cell in row for skip in [
                        "Copyright", "Notes", "Bank Statement", "Dummy Bank Statement"
                    ]):
                        continue
                    all_rows.append(row)

    if columns and all_rows:
        df = pd.DataFrame(all_rows, columns=columns)
        return df
    return None

# --- Pythonic extraction of full text for Gemini ---
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
        2. Bank Account Details:Bank Name, Account Nr, IFSC Code, Bank Branch Address
        Return in JSON format with keys: account_holder_details, bank_account_details.
        Text:
        {text}
        """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text

# --- Streamlit UI ---
st.title("Bank Statement Extractor")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type="pdf")

if uploaded_file:
    # Extract transactions with Python
    transactions_df = extract_transactions(uploaded_file)

    # Extract full text for Gemini
    text_content = extract_text(uploaded_file)

    # Show results
    if transactions_df is not None:
        st.subheader("Transactions Table (Python)")
        st.dataframe(transactions_df)
        csv = transactions_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Transactions CSV", csv, "transactions.csv", "text/csv")

        # Gemini for details only
        st.subheader("Account Holder & Bank Details (Gemini)")
        with st.spinner("Classifying with Gemini..."):
            result_json = classify_with_gemini(text_content, include_transactions=False)
            st.text(result_json)
    else:
        st.warning("No transactions table found using Python. Using Gemini for all data...")
        with st.spinner("Classifying with Gemini..."):
            result_json = classify_with_gemini(text_content, include_transactions=True)
            st.text(result_json)
