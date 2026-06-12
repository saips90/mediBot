import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.core.config import Settings, get_settings
from app.core.security import validate_api_keys
from app.generation.llm import build_llm
from app.generation.prompts import ANSWER_PROMPT, QUERY_REWRITE_PROMPT
from app.retrieval.reranker import build_reranker
from app.retrieval.retriever import build_retriever


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
        self.retriever = build_retriever(self.settings)
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
