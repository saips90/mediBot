from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker


def chunk_documents(documents: list[Document], embeddings) -> list[Document]:
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    return text_splitter.split_documents(documents)
