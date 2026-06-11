import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    data_dir = "/Users/v0s05ew/Downloads/Medibot_Assignment_Resources/mediassist_data"
    print(f"Loading data from {data_dir}...")
    
    pdf_loader = DirectoryLoader(data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    md_loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
    txt_loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader)

    documents = pdf_loader.load() + md_loader.load() + txt_loader.load()
    print(f"Loaded {len(documents)} documents.")

    print("Initializing HuggingFace embeddings for Semantic Chunking...")
    hf_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Semantically chunking text (this may take a while)...")
    text_splitter = SemanticChunker(hf_embeddings, breakpoint_threshold_type="percentile")
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} semantic chunks.")

    print("Initializing Sparse Embeddings (FastEmbed)...")
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

    if os.path.exists("./qdrant_db"):
        print("Clearing existing Qdrant DB...")
        shutil.rmtree("./qdrant_db")

    print("Storing semantic and sparse vectors in Qdrant DB natively...")
    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks, 
        embedding=hf_embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        path="./qdrant_db",
        collection_name="medibudi"
    )
    print("Ingestion complete. Data stored in ./qdrant_db")

if __name__ == "__main__":
    ingest_data()
