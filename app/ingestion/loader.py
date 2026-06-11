from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document


def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    loaders = [
        DirectoryLoader(str(data_dir), glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(str(data_dir), glob="**/*.md", loader_cls=TextLoader),
        DirectoryLoader(str(data_dir), glob="**/*.txt", loader_cls=TextLoader),
    ]

    documents: list[Document] = []
    for loader in loaders:
        documents.extend(loader.load())
    return documents
