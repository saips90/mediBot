import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.core.config import Settings, get_settings
from app.core.security import validate_api_keys
from app.generation.llm import build_llm
from app.generation.prompts import ANSWER_PROMPT, QUERY_REWRITE_PROMPT
from app.ingestion.vector_db import get_vectorstore
from app.retrieval.reranker import build_reranker
from app.retrieval.retriever import build_role_filter


def format_plain_text(answer: str) -> str:
    lines: list[str] = []

    for line in answer.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue

        if re.fullmatch(r"\|?[\s:|-]+\|?", stripped):
            continue

        if "|" in stripped:
            cells = [cell.strip() for cell in stripped.strip("|").split("|") if cell.strip()]
            if cells:
                lines.append("- " + ", ".join(cells))
            continue

        lines.append(stripped)

    text = "\n".join(lines)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace(" ", " ").replace("\u00a0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class MediBotRAG:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        validate_api_keys(self.settings)

        self.llm = build_llm(self.settings)
        self.vectorstore = get_vectorstore(self.settings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.settings.retrieval_k})
        self.reranker = build_reranker(self.settings)
        self.query_rewriter = QUERY_REWRITE_PROMPT | self.llm | StrOutputParser()

        def retrieve_with_rewrite(inputs):
            rewritten = self.query_rewriter.invoke({"question": inputs["question"]})
            docs = self.retriever.invoke(rewritten)
            docs = self.reranker.rerank(docs, rewritten)
            return {"context": docs, "question": inputs["question"]}

        self.chain = (
            RunnableLambda(retrieve_with_rewrite)
            | ANSWER_PROMPT
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        return format_plain_text(self.chain.invoke({"question": question}))

    def ask_with_role(self, question: str, role: str) -> dict[str, object]:
        rewritten = self.query_rewriter.invoke({"question": question})
        role_filter = build_role_filter(role)
        docs = self.vectorstore.similarity_search(
            rewritten,
            k=self.settings.retrieval_k,
            filter=role_filter,
        )
        docs = self.reranker.rerank(docs, rewritten)

        answer = (
            ANSWER_PROMPT
            | self.llm
            | StrOutputParser()
        ).invoke({"context": docs, "question": question})

        sources = []
        seen = set()
        for document in docs:
            metadata = document.metadata
            key = (
                metadata.get("source_document"),
                metadata.get("section_title"),
                metadata.get("collection"),
            )
            if key in seen:
                continue
            seen.add(key)
            sources.append(
                {
                    "source_document": metadata.get("source_document") or metadata.get("source"),
                    "section_title": metadata.get("section_title"),
                    "collection": metadata.get("collection"),
                    "chunk_type": metadata.get("chunk_type"),
                    "reranker_score": metadata.get("reranker_score"),
                }
            )

        return {
            "answer": format_plain_text(answer),
            "sources": sources,
            "retrieval_type": "hybrid_vector_reranked",
            "role": role,
            "rewritten_query": rewritten,
        }
