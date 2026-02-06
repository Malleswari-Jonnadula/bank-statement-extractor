# 🏦Bank Statement Extractor: PDF Data Extraction with Python & LLMs

A **Streamlit-based web application** that extracts **account holder details, bank details, and transaction tables** from bank statement PDFs using Python and a Large Language Model (LLM).
The system combines **rule-based PDF parsing** with **LLM-powered fallback extraction** for unstructured documents.

---

## 🚀 Features
- Upload PDF bank statements via **Streamlit UI**.
- Extracts:
  - Account Holder Details
  - Bank Account Details
  - Transaction Tables
- Automatically detects and parses transactions.
- Uses **Python-based extraction (`pdfplumber`)** for structured PDFs
- Uses **Groq LLM (LLaMA 3.1)** for intelligent extraction from unstructured text
- Download extracted transactions as **CSV**
- Optionally provides a **FastAPI endpoint** for programmatic uploads.
- Works **locally** and deployed on **Streamlit Cloud**.

---

## 💡Tech Stack

- **Python**
- **Streamlit**
- **pdfplumber**
- **Groq LLM (LLaMA 3.1)**
- **Pandas**
- **FastAPI**

---


## 📂 Project Structure

├── app.py           # Streamlit web app   
├── api.py           # FastAPI backend    
├── requirements.txt # Python dependencies   
├── README.md        # Documentation

---

## Setup
### 1. Clone the Repository
```bash
git clone https://github.com/Malleswari-Jonnadula/bank-statement-extractor.git
cd bank-statement-extractor
```
### 2. Create & Activate Virtual Environment
Windows :
```bash
python -m venv venv
venv\Scripts\activate
```
Mac/Linux :
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure API Key (Groq)
Create a .streamlit/secrets.toml file (locally):
```bash
GROQ_API_KEY = "your_groq_api_key_here"
```

---

## 2. Run Streamlit App Locally
```bash
streamlit run app.py
```
This will open your browser at:
[http://localhost:8501](http://localhost:8501)

---

## 3. Run API Locally
```bash
uvicorn api:app --reload
```
API Docs:
Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).
### API Usage
**Endpoint:** `POST /extract`  
**Content-Type:** `multipart/form-data`  
**Field:** `file` (PDF file)
### Example cURL request:
```bash
curl -X POST "http://localhost:8000/extract" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@Dummy-Bank-Statement.pdf;type=application/pdf"
```

---

## 🧠 Design Highlights

- **Modular LLM layer** – Easy to swap LLM providers (Gemini → Groq → others) without changing core logic  
- **Hybrid extraction approach** – Combines rule-based PDF parsing with LLM-based fallback extraction  
- **Robust JSON parsing & validation** – Ensures structured and reliable output from LLM responses  
- **Cloud-deployable architecture** – Designed to run seamlessly on Streamlit Cloud  

---

## 📌 Future Improvements

- **Schema-based JSON validation** for stricter data consistency  
- **OCR support** for scanned or image-based bank statements  
- **Multi-bank format optimization** to handle different statement layouts  
- **Caching mechanisms** to improve performance and reduce repeated LLM calls  

---

