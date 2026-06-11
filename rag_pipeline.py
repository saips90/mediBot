from app.rag_pipeline import MedibudiRAG


if __name__ == "__main__":
    rag = MedibudiRAG()
    print("Welcome to Medibudi RAG CLI!")
    while True:
        q = input("Ask a medical question (or 'q' to quit): ")
        if q.lower() == "q":
            break
        try:
            answer = rag.ask(q)
            print(f"\nMedibudi: {answer}\n")
        except Exception as exc:
            print(f"Error: {exc}")
