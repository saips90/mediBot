from app.core.config import Settings
from app.core.rbac import collections_for_role
from app.ingestion.vector_db import get_vectorstore
from qdrant_client import models


def build_retriever(settings: Settings):
    vectorstore = get_vectorstore(settings)
    return vectorstore.as_retriever(search_kwargs={"k": settings.retrieval_k})


def build_role_filter(role: str) -> models.Filter:
    collections = collections_for_role(role)
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.collection",
                match=models.MatchAny(any=collections),
            ),
            models.FieldCondition(
                key="metadata.access_roles",
                match=models.MatchValue(value=role),
            ),
        ]
    )
