# Medibudi

Medibudi is a backend-only FastAPI medical RAG service with document ingestion, hybrid Qdrant retrieval, and Groq-backed answer generation.

The mobile/frontend client should live in a separate React Native project and call this backend over HTTP.

## Project structure

```text
medibudi/
├── app/
│   ├── api/v1/          # FastAPI routers and endpoints
│   ├── core/            # Settings, logging, security helpers
│   ├── generation/      # LLM setup and prompt templates
│   ├── ingestion/       # Loading, chunking, and vector DB seeding
│   ├── retrieval/       # Retriever and reranker hooks
│   └── rag_pipeline.py  # RAG chain orchestration
├── data/
│   ├── raw/             # Source documents
│   └── processed/       # Optional intermediate files
├── notebooks/           # Experiments and prototyping
├── tests/               # Unit and integration tests
├── ingest.py            # Ingestion entry point
├── main.py              # FastAPI application entry point
└── requirements.txt
```

## API

- `GET /` returns service metadata.
- `GET /health` returns service health and whether the RAG pipeline initialized.
- `POST /api/chat` accepts `{ "message": "..." }` and returns `{ "reply": "..." }`.
- `GET /docs` opens the FastAPI Swagger documentation.

## Run locally

1. Create `.env` from `.env.example` and set `GROQ_API_KEY`.
2. Put source documents in `data/raw`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Build the vector store: `python ingest.py`.
5. Start the API: `python main.py`.
6. Open `http://localhost:8001/docs` for API docs.
