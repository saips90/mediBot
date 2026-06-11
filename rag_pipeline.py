import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class MedibudiRAG:
    def __init__(self):
        if not os.environ.get("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY environment variable not found. Please add it to your .env file.")
        
        print("Loading Qdrant Vector Store with Hybrid Search...")
        if not os.path.exists("./qdrant_db"):
            raise FileNotFoundError("Qdrant DB not found. Please run ingest.py first.")
            
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        client = QdrantClient(path="./qdrant_db")
        
        self.vectorstore = QdrantVectorStore(
            client=client, 
            collection_name="medibudi", 
            embedding=self.embeddings,
            sparse_embedding=self.sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            max_tokens=None,
            reasoning_format="parsed",
            timeout=None,
            max_retries=2,
        )
        
        # Query Rewriter Prompt — rephrases user query for better retrieval
        rewrite_template = """You are an expert at rephrasing questions into concise, keyword-rich search queries for a medical insurance knowledge base.

Rewrite the following question into a short, retrieval-optimised query using medical and insurance terminology.
Only return the rewritten query, nothing else.

Question: {question}
Rewritten query:"""
        self.rewrite_prompt = ChatPromptTemplate.from_template(rewrite_template)
        self.query_rewriter = self.rewrite_prompt | self.llm | StrOutputParser()

        # Main Answer Prompt
        template = """You are Medibudi, a friendly and precise medical AI assistant.

If the user sends a greeting or general message (like "hi", "hello", "how are you"), respond warmly and let them know you're here to help with medical questions.

For medical questions, answer ONLY based on the following retrieved context. If the context doesn't contain the answer, say you don't have enough information on that specific topic.

Context: {context}

Question: {question}
Answer:"""
        self.prompt = ChatPromptTemplate.from_template(template)

        # Full RAG Chain with Query Rewriting
        def retrieve_with_rewrite(inputs):
            rewritten = self.query_rewriter.invoke({"question": inputs["question"]})
            docs = self.retriever.invoke(rewritten)
            return {"context": docs, "question": inputs["question"]}

        self.chain = (
            RunnableLambda(retrieve_with_rewrite)
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
    def ask(self, question: str) -> str:
        return self.chain.invoke({"question": question})

if __name__ == "__main__":
    rag = MedibudiRAG()
    print("Welcome to Medibudi RAG CLI!")
    while True:
        q = input("Ask a medical question (or 'q' to quit): ")
        if q.lower() == 'q':
            break
        try:
            answer = rag.ask(q)
            print(f"\nMedibudi: {answer}\n")
        except Exception as e:
            print(f"Error: {e}")
