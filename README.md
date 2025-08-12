# Bank Statement Extractor: PDF Data Extraction with Python & Vertex AI

## What it does
- Extracts account holder & bank details and transactions (tabular) from bank statement PDFs.
- Uses pythonic extraction first; if transactions are not found, falls back to Gemini (Vertex AI).
- Streamlit UI + FastAPI endpoint for programmatic uploads.

## Local run (Streamlit)
1. Create .env with `GOOGLE_API_KEY=your_key`
2. pip install -r requirements.txt
3. streamlit run app.py 
4. Opens in browser (default):
   `http://localhost:8501`


## Run API locally
1. pip install -r requirements.txt
2. uvicorn api:app --reload
3. Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Usage

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

## Deployment
- Streamlit Cloud for `app.py`