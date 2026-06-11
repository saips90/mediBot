class NoOpReranker:
    def rerank(self, documents, query: str):
        return documents
