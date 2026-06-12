from app.rag_pipeline import MediBotRAG


if __name__ == "__main__":
    rag = MediBotRAG()
    print("Welcome to MediBot RAG CLI!")
    while True:
        q = input("Ask a medical question (or 'q' to quit): ")
        if q.lower() == "q":
            break
        try:
            answer = rag.ask(q)
            print(f"\nMediBot: {answer}\n")
        except Exception as exc:
            print(f"Error: {exc}")
