from langchain_groq import ChatGroq

from app.core.config import Settings


def build_llm(settings: Settings) -> ChatGroq:
    return ChatGroq(
        model=settings.llm_model,
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
        api_key=settings.groq_api_key,
    )
