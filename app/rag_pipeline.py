from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.core.config import Settings, get_settings
from app.core.security import validate_api_keys
from app.generation.llm import build_llm
from app.generation.prompts import ANSWER_PROMPT, QUERY_REWRITE_PROMPT
from app.retrieval.retriever import build_retriever


class MedibudiRAG:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        validate_api_keys(self.settings)

        self.llm = build_llm(self.settings)
        self.retriever = build_retriever(self.settings)
        self.query_rewriter = QUERY_REWRITE_PROMPT | self.llm | StrOutputParser()

        def retrieve_with_rewrite(inputs):
            rewritten = self.query_rewriter.invoke({"question": inputs["question"]})
            docs = self.retriever.invoke(rewritten)
            return {"context": docs, "question": inputs["question"]}

        self.chain = (
            RunnableLambda(retrieve_with_rewrite)
            | ANSWER_PROMPT
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        return self.chain.invoke({"question": question})
