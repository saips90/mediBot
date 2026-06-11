import shutil
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient

from app.core.config import Settings


def build_dense_embeddings(settings: Settings) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def build_sparse_embeddings(settings: Settings) -> FastEmbedSparse:
    return FastEmbedSparse(model_name=settings.sparse_embedding_model)


def get_vectorstore(settings: Settings) -> QdrantVectorStore:
    if not Path(settings.qdrant_path).exists():
        raise FileNotFoundError("Qdrant DB not found. Please run ingest.py first.")

    client = QdrantClient(path=str(settings.qdrant_path))
    return QdrantVectorStore(
        client=client,
        collection_name=settings.collection_name,
        embedding=build_dense_embeddings(settings),
        sparse_embedding=build_sparse_embeddings(settings),
        retrieval_mode=RetrievalMode.HYBRID,
    )


def seed_vectorstore(documents, settings: Settings, reset: bool = True) -> QdrantVectorStore:
    if reset and Path(settings.qdrant_path).exists():
        shutil.rmtree(settings.qdrant_path)

    return QdrantVectorStore.from_documents(
        documents=documents,
        embedding=build_dense_embeddings(settings),
        sparse_embedding=build_sparse_embeddings(settings),
        retrieval_mode=RetrievalMode.HYBRID,
        path=str(settings.qdrant_path),
        collection_name=settings.collection_name,
    )
