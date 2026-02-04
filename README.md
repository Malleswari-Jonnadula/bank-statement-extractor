# 🏦Bank Statement Extractor: PDF Data Extraction with Python & Vertex AI

Extracts **account holder details, bank details, and transaction tables** from bank statement PDFs. 
Uses:
- **Pythonic extraction** (via `pdfplumber`) for structured tables.
- **Gemini (Google AI)** for fallback extraction when transactions aren’t found.

---

## 🚀 Features
- Upload PDF bank statements via **Streamlit UI**.
- Automatically detects and parses transactions.
- Falls back to **Google Gemini** AI for unstructured PDFs.
- Optionally provides a **FastAPI endpoint** for programmatic uploads.
- Works **locally** and on **Streamlit Cloud**.

---

## 📂 Project Structure

├── app.py # Streamlit web app   
├── api.py # FastAPI backend    
├── requirements.txt # Python dependencies   
├── README.md # Documentation

---

## 1. Local Setup
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
### 4. Configure Environment Variables
Create a .env file in the project root :
```bash
GOOGLE_API_KEY=your_google_api_key_here
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

  
