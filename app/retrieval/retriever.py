from app.core.config import Settings
from app.ingestion.vector_db import get_vectorstore


def build_retriever(settings: Settings):
    vectorstore = get_vectorstore(settings)
    return vectorstore.as_retriever(search_kwargs={"k": settings.retrieval_k})
