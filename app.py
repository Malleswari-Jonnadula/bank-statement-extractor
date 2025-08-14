import streamlit as st
import pdfplumber
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import json
import re

# Optional fallback libraries
try:
    import camelot
except ImportError:
    camelot = None

try:
    import tabula
except ImportError:
    tabula = None

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found! Set it in .env or Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# --- PDF Table Extraction ---
# --- PDF Table Extraction ---
def extract_transactions(pdf_file):
    all_rows = []
    columns = None

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                if columns is None:
                    columns = table[0]
                for row in table[1:]:
                    if len(row) == len(columns):
                        all_rows.append(row)

    if columns and all_rows:
        return pd.DataFrame(all_rows, columns=columns)
    return None  # No table found


# --- Extract full text for Gemini ---
def extract_text(pdf_file):
    text_content = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
    return text_content

# --- Gemini Classification ---
def classify_with_gemini(text, include_transactions=False):
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
        Give account holder details and related and bank account details related.
        Return keys: account_holder_details, bank_account_details.
        Text:
        {text}
        """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text

# --- Robust Gemini JSON Parser ---
def clean_and_parse_gemini(json_text):
    try:
        match = re.search(r'(\{.*\})', json_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json.loads(json_str)
        else:
            st.error("No JSON object found in Gemini output")
            st.text(json_text)
            return None
    except Exception as e:
        st.error(f"Failed to parse Gemini JSON output: {e}")
        st.text(json_text)
        return None

# --- Render Gemini Tables ---
def render_gemini_tables(json_text):
    data = clean_and_parse_gemini(json_text)
    if not data:
        return

    if "account_holder_details" in data:
        st.subheader("Account Holder Details")
        st.table(pd.DataFrame([data["account_holder_details"]]))

    if "bank_account_details" in data:
        st.subheader("Bank Account Details")
        st.table(pd.DataFrame([data["bank_account_details"]]))

    if "transactions" in data:
        st.subheader("Transactions Table (Gemini)")
        transactions = data["transactions"]
        if isinstance(transactions, list) and len(transactions) > 0 and isinstance(transactions[0], dict):
            df_trans = pd.DataFrame(transactions)
            st.dataframe(df_trans)
            csv = df_trans.to_csv(index=False).encode("utf-8")
            st.download_button("Download Gemini Transactions CSV", csv, "gemini_transactions.csv", "text/csv")
        else:
            st.warning("No valid transactions found in Gemini output")

# --- Streamlit UI ---
st.title("Bank Statement Extractor")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type="pdf")

if uploaded_file:
    # Python table extraction
    transactions_df = extract_transactions(uploaded_file)

    # Full text for Gemini
    text_content = extract_text(uploaded_file)

    if transactions_df is not None and not transactions_df.empty:
        st.subheader("Transactions Table (Python)")
        st.dataframe(transactions_df)
        csv = transactions_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Transactions CSV", csv, "transactions.csv", "text/csv")

        st.subheader("Account Holder & Bank Details (Gemini)")
        with st.spinner("Classifying with Gemini..."):
            result_json = classify_with_gemini(text_content, include_transactions=False)
            render_gemini_tables(result_json)
    else:
        st.warning("No transactions table found using Python. Using Gemini for all data...")
        with st.spinner("Classifying with Gemini..."):
            result_json = classify_with_gemini(text_content, include_transactions=True)
            render_gemini_tables(result_json)
