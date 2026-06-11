# Medibudi

Medibudi is a full-stack medical RAG project with a FastAPI backend and a React Native frontend.

The backend handles document ingestion, hybrid Qdrant retrieval, and Groq-backed answer generation. The frontend is an Expo React Native chat app that calls the backend over HTTP.

## Project structure

```text
medibudi/
├── app/                  # Backend application code
│   ├── api/v1/           # FastAPI routers and endpoints
│   ├── core/             # Settings, logging, security helpers
│   ├── generation/       # LLM setup and prompt templates
│   ├── ingestion/        # Loading, chunking, and vector DB seeding
│   ├── retrieval/        # Retriever and reranker hooks
│   └── rag_pipeline.py   # RAG chain orchestration
├── data/
│   ├── raw/              # Source documents
│   └── processed/        # Optional intermediate files
├── frontend/             # Expo React Native mobile app
│   ├── App.js
│   ├── src/
│   └── package.json
├── notebooks/            # Experiments and prototyping
├── tests/                # Unit and integration tests
├── ingest.py             # Backend ingestion entry point
├── main.py               # FastAPI application entry point
└── requirements.txt
```

## Backend API

- `GET /` returns service metadata.
- `GET /health` returns service health and whether the RAG pipeline initialized.
- `POST /api/chat` accepts `{ "message": "..." }` and returns `{ "reply": "..." }`.
- `GET /docs` opens the FastAPI Swagger documentation.

## Run backend

```bash
cp .env.example .env
# Set GROQ_API_KEY in .env
pip install -r requirements.txt
python ingest.py
python main.py
```

Backend runs at `http://localhost:8001` by default.

## Run frontend

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Set `EXPO_PUBLIC_API_BASE_URL` in `frontend/.env` based on where the app runs:

- iOS simulator: `http://localhost:8001`
- Android emulator: `http://10.0.2.2:8001`
- Physical phone: `http://<your-computer-lan-ip>:8001`
