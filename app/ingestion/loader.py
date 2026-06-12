from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


def load_pdf_documents(data_dir: Path) -> list[Document]:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise ImportError(
            "Docling is required for PDF ingestion. Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    converter = DocumentConverter()
    documents: list[Document] = []

    for pdf_path in sorted(data_dir.rglob("*.pdf")):
        result = converter.convert(str(pdf_path))
        markdown = result.document.export_to_markdown()

        if not markdown.strip():
            continue

        documents.append(
            Document(
                page_content=markdown,
                metadata={
                    "source": str(pdf_path),
                    "loader": "docling",
                    "format": "pdf",
                },
            )
        )

    return documents


def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    loaders = [
        DirectoryLoader(str(data_dir), glob="**/*.md", loader_cls=TextLoader),
        DirectoryLoader(str(data_dir), glob="**/*.txt", loader_cls=TextLoader),
    ]

    documents = load_pdf_documents(data_dir)
    for loader in loaders:
        documents.extend(loader.load())
    return documents
