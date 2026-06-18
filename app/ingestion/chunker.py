from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents: list[Document], embeddings) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1600,
        chunk_overlap=200,
        separators=["\n## ", "\n# ", "\n\n", "\n", ". ", " "],
    )

    chunks: list[Document] = []
    for document in documents:
        if len(document.page_content) <= 1800:
            chunks.append(document)
            continue
        chunks.extend(text_splitter.split_documents([document]))
    return chunks
