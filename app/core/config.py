from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = "MediBot RAG API"
    api_v1_prefix: str = "/api"

    groq_api_key: str | None = None
    llm_model: str = "openai/gpt-oss-20b"
    embedding_model: str = "all-MiniLM-L6-v2"
    sparse_embedding_model: str = "Qdrant/bm25"

    collection_name: str = "medibudi"
    qdrant_path: Path = ROOT_DIR / "qdrant_db"
    data_dir: Path = ROOT_DIR / "data" / "raw"
    retrieval_k: int = 5
    reranker_enabled: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"
    reranker_top_n: int = 3

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def resolve_paths(self):
        for field_name in ("qdrant_path", "data_dir"):
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, ROOT_DIR / path)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
