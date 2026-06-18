from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.ingestion.chunker import chunk_documents
from app.ingestion.loader import load_documents
from app.ingestion.vector_db import build_dense_embeddings, seed_vectorstore

logger = get_logger(__name__)


def ingest_data(settings: Settings | None = None) -> None:
    settings = settings or get_settings()

    logger.info("Loading data from %s", settings.data_dir)
    documents = load_documents(settings.data_dir)
    logger.info("Loaded %s documents", len(documents))

    logger.info("Initializing embeddings")
    embeddings = build_dense_embeddings(settings)

    logger.info("Applying bounded text splitting to oversized chunks")
    chunks = chunk_documents(documents, embeddings)
    logger.info("Split into %s semantic chunks", len(chunks))

    logger.info("Storing dense and sparse vectors in Qdrant")
    seed_vectorstore(chunks, settings=settings, reset=True)
    logger.info("Ingestion complete. Data stored in %s", settings.qdrant_path)
