# Content Recommendation Engine

FastAPI service and Streamlit UI that provide PDF recommendations using three strategies: collaborative filtering (ALS), sequential behavior (Markov chains), and semantic similarity (E5 embeddings + Qdrant).

**Features**
- Three recommendation models with a single API.
- Content-based search over embedded PDF chunks stored in a local Qdrant collection.
- MySQL-backed user reading history for ALS and Markov models.
- Streamlit UI for quick comparisons across models.

**Repository Layout**
- `main.py` FastAPI entrypoint with model startup and routes.
- `api/` HTTP routes for ALS, Markov, and content-based recommendations.
- `core/` model implementations and training/refresh logic.
- `embeddings/` E5 embedding wrapper.
- `vectorstore/` local Qdrant client and collection management.
- `helpers/` SQL queries, data loading, and chunking helpers.
- `utils/` S3 access, PDF parsing, DB utilities, preprocessing.
- `scripts/` ingestion and training utilities.
- `frontend/` Streamlit UI.

**How It Works**
- ALS and Markov models train from MySQL reading history (`pdf_time_tracks`, `pdfs`, `users`, `profiles`).
- Content-based recommendations read the latest PDF from S3, extract text, chunk it, embed with `intfloat/multilingual-e5-large`, search Qdrant, and rank top hits.
- Qdrant runs in embedded mode and stores vectors in `./qdrant_data`.

**API Endpoints**
- `GET /` Health check.
- `GET /als/recommend/{email}` ALS recommendations for the most recent user session.
- `GET /recommend/markov/{email}` Markov recommendations based on last read PDF.
- `GET /recommend/content/{email}` Content-based recommendations using Qdrant similarity.

**Quick Start**
1. Create and activate a virtual environment.
2. Install dependencies.
3. Set environment variables in `.env`.
4. Start the API.
5. Run the Streamlit UI.

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

```bash
streamlit run frontend/app.py
```

The UI expects the API at `http://localhost:8001`. Update `BASE_URL` in `frontend/app.py` if you use a different host or port.

**Environment Variables**
Set these in `.env` (do not commit secrets).
- `MYSQL_USER`
- `MYSQL_PW`
- `MYSQL_DB`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `AWS_BUCKET_NAME`
- `API_AUTH`
- `API_URL`
- `PREVIEW_ID`

**Data Ingestion (Qdrant)**
Use the ingestion script to build vectors from `output.csv`.

```bash
python scripts/manual_train.py
```

This reads `output.csv`, cleans text, chunks it, embeds with E5, and upserts into Qdrant.

**Notes**
- The Markov model refreshes automatically every hour (`core/model_registry.py`).
- ALS training runs at API startup (`main.py`).
- If you use a fresh DB, ensure the referenced tables and columns exist as defined in `helpers/sql_helpers.py`.
- Additional Python packages are imported in the codebase beyond `requirements.txt` (for example `pandas`, `sqlalchemy`, `pymysql`, `boto3`, `qdrant-client`, `implicit`, `scipy`, `streamlit`, `requests`, `pdfplumber`). Install them as needed based on your runtime errors.

**Security**
This repo uses environment variables for credentials. Add `.env` to `.gitignore` and prefer an `.env.example` for sharing non-secret defaults.
