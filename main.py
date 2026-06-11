from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logger import get_logger
from app.rag_pipeline import MedibudiRAG

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag_pipeline = None
    try:
        app.state.rag_pipeline = MedibudiRAG(settings)
        logger.info("Medibudi RAG Pipeline initialized successfully")
    except Exception as exc:
        logger.warning("RAG Pipeline initialization failed. Did you run ingest.py? Error: %s", exc)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "chat_endpoint": f"{settings.api_v1_prefix}/chat",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "rag_ready": app.state.rag_pipeline is not None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
