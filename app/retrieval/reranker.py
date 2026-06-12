from langchain_core.documents import Document

from app.core.config import Settings


class NoOpReranker:
    def rerank(self, documents: list[Document], query: str) -> list[Document]:
        return documents


class CrossEncoderReranker:
    def __init__(self, model_name: str, top_n: int):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(model_name)
        self.top_n = top_n

    def rerank(self, documents: list[Document], query: str) -> list[Document]:
        if not documents:
            return documents

        pairs = [(query, document.page_content) for document in documents]
        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores, strict=False),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        reranked_documents: list[Document] = []
        for document, score in ranked[: self.top_n]:
            document.metadata["reranker_score"] = float(score)
            reranked_documents.append(document)

        return reranked_documents


def build_reranker(settings: Settings):
    if not settings.reranker_enabled:
        return NoOpReranker()

    return CrossEncoderReranker(
        model_name=settings.reranker_model,
        top_n=settings.reranker_top_n,
    )
