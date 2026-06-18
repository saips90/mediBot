from pathlib import Path
import re

from langchain_core.documents import Document

from app.core.rbac import collection_from_path


def _chunk_type(text: str) -> str:
    if "|" in text and re.search(r"\|.*\|", text):
        return "table"
    if text.lstrip().startswith("#"):
        return "heading"
    return "text"


def _section_title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        markdown_heading = re.match(r"^#{1,6}\s+(.+)$", stripped)
        if markdown_heading:
            return markdown_heading.group(1).strip()
        if len(stripped) <= 90:
            return stripped
        break
    return fallback


def _metadata_for_path(path: Path, data_dir: Path, section_title: str, chunk_type: str, loader: str) -> dict:
    access = collection_from_path(path, data_dir)
    return {
        "source": str(path),
        "source_document": path.name,
        "collection": access.collection,
        "access_roles": access.access_roles,
        "section_title": section_title,
        "chunk_type": chunk_type,
        "loader": loader,
        "format": path.suffix.lstrip(".").lower() or "text",
    }


def _split_markdown_sections(text: str, fallback_title: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = fallback_title
    current_lines: list[str] = []

    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if heading and current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))
            current_lines = []
        if heading:
            current_title = heading.group(1).strip()
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return [(title, body) for title, body in sections if body]


def load_pdf_documents(data_dir: Path) -> list[Document]:
    try:
        from docling.document_converter import DocumentConverter
        from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker
    except ImportError as exc:
        raise ImportError(
            "Docling is required for PDF ingestion. Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    converter = DocumentConverter()
    chunker = HierarchicalChunker()
    documents: list[Document] = []

    for pdf_path in sorted(data_dir.rglob("*.pdf")):
        result = converter.convert(str(pdf_path))
        for chunk in chunker.chunk(dl_doc=result.document):
            text = chunk.text.strip()
            if not text:
                continue

            headings = getattr(chunk.meta, "headings", None) or []
            section_title = headings[-1] if headings else _section_title_from_text(text, pdf_path.stem)
            context = f"Document: {pdf_path.name}\nSection: {section_title}\n\n{text}"
            documents.append(
                Document(
                    page_content=context,
                    metadata=_metadata_for_path(
                        pdf_path,
                        data_dir,
                        section_title=section_title,
                        chunk_type=_chunk_type(text),
                        loader="docling_hierarchical_chunker",
                    ),
                )
            )

    return documents


def load_text_documents(data_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted([*data_dir.rglob("*.md"), *data_dir.rglob("*.txt")]):
        text = path.read_text(encoding="utf-8")
        for section_title, body in _split_markdown_sections(text, path.stem):
            context = f"Document: {path.name}\nSection: {section_title}\n\n{body}"
            documents.append(
                Document(
                    page_content=context,
                    metadata=_metadata_for_path(
                        path,
                        data_dir,
                        section_title=section_title,
                        chunk_type=_chunk_type(body),
                        loader="text",
                    ),
                )
            )
    return documents


def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    documents = load_pdf_documents(data_dir)
    documents.extend(load_text_documents(data_dir))
    return documents
