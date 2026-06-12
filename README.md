# MediBot

MediBot is a full-stack Retrieval-Augmented Generation (RAG) application for medical and insurance document question answering.

The project combines a FastAPI backend, Docling-based PDF ingestion, semantic chunking, hybrid Qdrant retrieval, Groq-backed LLM generation, and an Expo web chat frontend. It is designed as a practical reference project for interviews, resume discussions, and future RAG system design decisions.

## What This Project Demonstrates

- End-to-end RAG pipeline design.
- PDF and Markdown ingestion for table-heavy medical insurance documents.
- Docling conversion to preserve PDF tables as Markdown-like structured text.
- Semantic chunking instead of naive fixed-size splitting.
- Dense + sparse hybrid retrieval with Qdrant.
- Query rewriting before retrieval.
- Grounded response generation with explicit missing-context handling.
- Plain-text answer cleanup for frontend usability.
- FastAPI backend with health and chat endpoints.
- Expo web frontend for browser-based chat.

## Architecture

```text
User
  |
  v
Expo Web Frontend
  |
  v
FastAPI /api/chat
  |
  v
Query Rewrite Prompt
  |
  v
Qdrant Hybrid Retriever
  |-- Dense semantic vectors: sentence-transformers/all-MiniLM-L6-v2
  |-- Sparse keyword vectors: Qdrant/bm25
  |
  v
Top-k Retrieved Chunks
  |
  v
Cross-Encoder Reranker
  |-- Model: cross-encoder/ms-marco-MiniLM-L6-v2
  |-- Keeps best RERANKER_TOP_N chunks
  |
  v
Reranked Context
  |
  v
Grounded Answer Prompt
  |
  v
Groq LLM
  |
  v
Plain-text cleanup
  |
  v
Frontend answer
```

## Project Structure

```text
medibudi/
├── app/
│   ├── api/v1/             # FastAPI router and chat endpoint
│   ├── core/               # Settings, logging, API key validation
│   ├── generation/         # LLM setup and prompt templates
│   ├── ingestion/          # Docling loading, chunking, Qdrant seeding
│   ├── retrieval/          # Retriever and reranker extension point
│   └── rag_pipeline.py     # RAG chain orchestration
├── data/
│   ├── raw/                # Local sample documents
│   └── processed/          # Optional intermediate artifacts
├── frontend/               # Expo web chat UI
├── ingest.py               # Rebuilds Qdrant from source documents
├── main.py                 # FastAPI app entrypoint
├── rag_pipeline.py         # CLI entrypoint
└── requirements.txt
```

## Backend API

- `GET /` returns service metadata.
- `GET /health` returns service health and whether the RAG pipeline initialized.
- `POST /api/chat` accepts `{ "message": "..." }` and returns `{ "reply": "..." }`.
- `GET /docs` opens FastAPI Swagger documentation.

## Setup

Create and configure `.env`:

```bash
cp .env.example .env
```

Required values:

```text
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=all-MiniLM-L6-v2
SPARSE_EMBEDDING_MODEL=Qdrant/bm25
COLLECTION_NAME=medibudi
DATA_DIR=/path/to/your/document/folder
QDRANT_PATH=qdrant_db
RETRIEVAL_K=5
RERANKER_ENABLED=true
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L6-v2
RERANKER_TOP_N=3
```

Install backend dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run ingestion:

```bash
python ingest.py
```

Start backend:

```bash
python main.py
```

Backend runs at:

```text
http://localhost:8001
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run web
```

Frontend runs at:

```text
http://localhost:8083
```

Set `frontend/.env`:

```text
EXPO_PUBLIC_API_BASE_URL=http://localhost:8001
```

## Ingestion Pipeline

The ingestion pipeline does this:

1. Loads PDFs with Docling.
2. Converts PDFs into Markdown-style structured text.
3. Loads Markdown and text documents with LangChain text loaders.
4. Applies semantic chunking.
5. Creates dense embeddings.
6. Creates sparse BM25-style embeddings.
7. Stores both in Qdrant using hybrid retrieval mode.

Current implementation:

- PDF loader: `docling.document_converter.DocumentConverter`
- Markdown/text loaders: LangChain `TextLoader`
- Chunker: LangChain `SemanticChunker`
- Dense embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Sparse embeddings: `Qdrant/bm25`
- Vector database: Qdrant local persistence

## Why Docling?

The source documents include PDFs with tables, policy schedules, billing codes, room rent limits, and insurance rules. Basic PDF text extraction often flattens tables into messy text, which can lose row-column relationships.

Docling is used because it handles document layout better and exports structured content that preserves tables more effectively. This improves retrieval for questions like:

- "What is eligibility for general ward?"
- "What is the package rate for cataract?"
- "Which room category applies for 5 lakh sum insured?"

## Why Semantic Chunking?

This project uses semantic chunking because medical and insurance documents often contain sections where the meaning changes by topic, not by fixed character count.

Semantic chunking tries to split documents where the embedding meaning shifts. That helps keep related rows, explanations, and policy clauses together.

Alternative chunking strategies:

- Fixed-size chunking: Simple and predictable, but can split tables or clauses in the middle.
- Recursive character splitting: Better than fixed-size because it respects separators like headings and paragraphs, but it is still mostly syntax-based.
- Sentence splitting: Clean boundaries, but often too small for RAG because individual sentences may lose context.
- Paragraph splitting: Good for prose, but weak for large tables or long policy sections.
- Semantic chunking: More expensive, but better when documents contain topic shifts, mixed layout, and dense policies.

Why not recursive splitting here?

Recursive splitting is a strong default and would also work. I chose semantic chunking because the data has mixed clinical, billing, policy, and tabular sections. The goal is to keep meaning-based sections together rather than split by size alone.

## Chunk Size And Overlap

This implementation uses `SemanticChunker`, so it does not manually set a traditional chunk size and overlap like recursive splitting.

If using recursive splitting, a typical starting point would be:

- Chunk size: 500-1000 tokens.
- Overlap: 50-150 tokens.

Tradeoffs:

- Too small: Retrieval may miss important context, and the LLM sees fragments.
- Too large: Retrieval becomes noisy, more tokens are sent to the LLM, and unrelated facts may enter the context.
- Too much overlap: Higher storage cost and repeated content.
- Too little overlap: Boundary facts can be lost.

## Why This Embedding Model?

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Reasons:

- Lightweight and fast for local development.
- Good enough semantic quality for a portfolio-scale RAG app.
- Easy to run without a paid embedding API.
- Works well with Qdrant local persistence.

Alternatives:

- OpenAI text-embedding models: Strong quality, but require API usage and cost.
- BAAI/bge-small or bge-base: Strong retrieval models, good alternative for local use.
- E5 models: Good for query-document retrieval, but need correct query/document prefixes.
- Instructor models: Useful for task-specific embeddings, but heavier.

For production, I would benchmark embeddings with real question-answer pairs instead of choosing only by model popularity.

## Why Qdrant?

Qdrant is used because it supports:

- Local persistence.
- Dense vector search.
- Sparse vector search.
- Hybrid retrieval.
- Metadata payloads and filtering.
- Easy local development.
- A path to production deployment.

Compared with alternatives:

- FAISS: Very fast local vector search, but weaker built-in persistence, metadata filtering, and sparse/hybrid support.
- Chroma: Easy for prototypes, but Qdrant gives stronger production-style vector DB features.
- Pinecone: Managed and scalable, but paid/external and less ideal for a local resume project.
- Weaviate: Powerful hybrid search and schema features, but heavier to run.
- Milvus: Strong at scale, but more operationally complex for this project size.

For this use case, the most important factors are:

- Ease of setup.
- Local persistence.
- Hybrid dense + sparse retrieval.
- Metadata support.
- Clear production migration path.

## Dense, Sparse, And Hybrid Retrieval

This project uses hybrid retrieval.

Dense retrieval:

- Uses embeddings to find semantically similar content.
- Good for paraphrased queries.
- Example: "room category for 3 lakh cover" can match "sum insured ₹3-5 lakh".

Sparse retrieval:

- Uses keyword-style matching such as BM25.
- Good for exact terms, codes, room names, policy labels, and medical abbreviations.
- Example: "PROC-CARD-01" or "general ward".

Hybrid retrieval:

- Combines dense and sparse retrieval.
- Better for documents that contain both natural language and exact tabular terms.
- Useful for medical insurance data because both meaning and exact wording matter.

## Top-k And Top-p

Top-k appears in two different contexts:

Retrieval top-k:

- The retriever returns the top `k` most relevant chunks.
- In this project, `RETRIEVAL_K=5`.
- Higher k improves recall but can add noise.
- Lower k improves precision but may miss context.

Generation top-k/top-p:

- These are decoding parameters used by some LLMs to control token sampling.
- Top-p chooses from the smallest token set whose probability mass reaches p.
- Top-k limits sampling to the k most likely next tokens.

This project mainly controls generation determinism with temperature. Retrieval top-k is configured separately from LLM sampling.

## LLM Temperature

This project uses low temperature:

```python
temperature=0
```

Why:

- RAG answers should be factual and grounded.
- Medical and insurance answers should avoid creative variation.
- Deterministic output is easier to test and debug.

Temperature behavior:

- 0: Most deterministic. Best for factual QA and extraction.
- 0.3: Slight variation while staying focused.
- 0.7: More creative and diverse. Useful for drafting or brainstorming.
- 1.0: Highly varied. More risk of hallucination.

Higher temperature is better for:

- Brainstorming.
- Marketing copy.
- User-facing creative writing.
- Generating multiple alternative phrasings.

Higher temperature is worse for:

- Medical QA.
- Insurance policy interpretation.
- Compliance-sensitive answers.
- RAG systems where faithfulness matters.

## Reducing Hallucination

This project reduces hallucination by:

- Retrieving relevant context before generation.
- Asking the model to answer only from retrieved context.
- Explicitly instructing the model to say it lacks information when context is missing.
- Using low temperature.
- Cleaning output formatting without adding new facts.

Additional production improvements:

- Add source citations.
- Keep reranking enabled and tune `RERANKER_TOP_N` using evaluation data.
- Add context relevance checks.
- Add answer faithfulness evaluation.
- Add guardrails for medical disclaimers.
- Add "I found X, but not Y" style responses for partial evidence.

## Query Rewriting

The system rewrites user questions into short retrieval-optimized queries before searching Qdrant.

Why:

- Users ask vague or conversational questions.
- Insurance documents use specific terms like "sum insured", "room rent", "sub-limit", and "proportionate deduction".
- Rewriting can improve retrieval recall.

Example:

```text
User: which is better general ward or something else?
Rewritten: room rent eligibility general ward twin sharing single private sum insured proportionate deduction
```

Risks:

- A bad rewrite can drift away from the user question.
- The rewrite should stay concise and preserve intent.

## Handling Vague Queries

When the query is vague:

- Query rewriting adds domain-specific terms.
- Hybrid retrieval catches both exact words and semantic meaning.
- The generator should answer only from available context.
- If the context is insufficient, it should say so instead of guessing.

Example:

```text
Question: general ward
Answer: General ward is eligible when the sum insured is under ₹3 lakh...
```

## Reranking

The repo includes an optional cross-encoder reranker after Qdrant retrieval.

Current reranker:

```text
cross-encoder/ms-marco-MiniLM-L6-v2
```

Flow:

1. Qdrant hybrid retrieval returns the top `RETRIEVAL_K` candidate chunks.
2. The reranker scores each `(query, chunk)` pair.
3. The backend keeps the best `RERANKER_TOP_N` chunks.
4. Only reranked context is sent to the answer prompt.

Why reranking is useful:

- The initial retriever may return a broad set of candidates.
- The cross-encoder reranker can compare the query and each chunk more carefully than vector similarity alone.
- This improves precision, especially when many chunks contain similar terms.

When reranking helps most:

- When the corpus grows larger.
- When top retrieved chunks are often related but not exact.
- When similar documents contain conflicting policy details.
- When high precision matters more than latency.

Candidate alternatives:

- BAAI/bge-reranker-base.
- Cohere rerank.
- Mixedbread rerank models.
- Cross-encoder/ms-marco style models.

Tradeoff:

- Better precision.
- More latency and compute cost.

## Metadata Filtering

Qdrant supports metadata payloads. The ingestion pipeline stores source metadata such as the file path and loader.

Possible filters:

- Department: billing, clinical, nursing, HR.
- File type: PDF, Markdown, text.
- Source document.
- Policy version.
- Date.
- Region or hospital.

Current implementation does not expose user-facing metadata filters yet, but the vector DB choice supports adding them.

## Improving Recall Without Hurting Precision

Options:

- Increase retrieval `k`.
- Use hybrid search.
- Rewrite the query.
- Use the cross-encoder reranker already included in the pipeline.
- Add multi-query retrieval for broader recall if needed.
- Use metadata filters.
- Improve chunking.
- Improve document conversion quality.

The safest path is usually:

1. Improve ingestion and chunk quality.
2. Use hybrid retrieval.
3. Retrieve slightly more chunks.
4. Rerank before sending context to the LLM.

## Generator Design

The answer prompt has three main responsibilities:

1. Define the assistant identity.
2. Restrict answers to retrieved context.
3. Define behavior when context is missing.

The prompt tells the model:

- It is MediBot.
- It should answer only from retrieved context.
- If the context does not contain the answer, it should say it does not have enough information.
- It should use plain text, not Markdown tables or raw formatting.

## Handling Missing Context

If retrieved context does not contain the answer, the model should not infer or invent.

Example:

```text
Question: What is the exact cost of general ward?
Answer: The provided documents do not specify the exact cost for a general ward.
```

This distinction matters:

- The docs specify eligibility.
- The docs do not specify exact price.

So the correct answer should explain what is known and what is missing.

## Response Formatting

The frontend currently renders plain text chat bubbles. Because LLMs often return Markdown by default, the backend includes a cleanup step that:

- Removes bold markers.
- Removes inline backticks.
- Converts Markdown table rows into simple plain-text lines.
- Normalizes spacing.

This keeps the UI readable without requiring a Markdown renderer.

## Interview Q&A Reference

### Why did you choose low temperature?

Because the app answers medical and insurance document questions. The priority is grounded, repeatable, factual output, not creativity.

### What happens at different temperatures?

- 0: Deterministic and factual.
- 0.3: Slightly more natural variation.
- 0.7: More creative but less predictable.
- 1.0: High randomness and higher hallucination risk.

### When would higher temperature be better?

For brainstorming, summaries with multiple styles, marketing text, or creative assistant behavior. Not ideal for policy QA.

### How do you reduce hallucination in RAG?

Retrieve good context, use low temperature, instruct the model to answer only from context, handle missing information explicitly, and evaluate answer faithfulness.

### Why did you choose semantic chunking?

Because the documents include mixed sections, policies, tables, and clinical/billing topics. Semantic chunking attempts to split where meaning changes, which is better than blindly splitting by character count.

### Why not fixed-size chunking?

Fixed-size chunks are simple but can split tables, clauses, or policy explanations in the middle.

### Why not sentence splitting?

Sentences are often too small and lose surrounding policy context.

### Why not paragraph splitting?

Paragraphs are useful for prose, but tables and PDF layouts do not always map cleanly to paragraphs.

### Why not recursive splitting?

Recursive splitting is a good baseline. I chose semantic chunking because this corpus benefits from meaning-based boundaries. If latency or ingestion cost became an issue, recursive splitting would be a practical fallback.

### How did you decide chunk size and overlap?

With semantic chunking, I do not manually set chunk size and overlap. If using recursive splitting, I would start around 500-1000 tokens with 50-150 tokens overlap and tune using retrieval evaluation.

### What happens if chunks are too small?

The retriever may return fragments without enough context, causing incomplete answers.

### What happens if chunks are too large?

The retriever may return noisy chunks with unrelated information, increasing token cost and hallucination risk.

### Why did you choose all-MiniLM-L6-v2?

It is lightweight, fast, local, and good enough for a portfolio-scale RAG project. It avoids embedding API cost.

### What embedding alternatives did you consider?

OpenAI embeddings, BGE, E5, and Instructor models. I would benchmark them if moving toward production.

### Why Qdrant?

Qdrant supports persistent local storage, dense vectors, sparse vectors, hybrid retrieval, and metadata filtering. It is more production-representative than a purely in-memory local index.

### Why not Chroma?

Chroma is easy for prototypes, but Qdrant has stronger hybrid retrieval and production-oriented vector DB capabilities.

### Why not FAISS?

FAISS is very fast, but it does not provide the same out-of-the-box persistence, filtering, sparse retrieval, and API-style database features.

### Why not Pinecone?

Pinecone is managed and scalable, but it adds external dependency and cost. This project prioritizes local reproducibility.

### Why not Weaviate or Milvus?

Both are strong, but heavier operationally for this project. Qdrant gives the needed features with simpler setup.

### What matters most for this use case?

Ease of setup, local persistence, hybrid retrieval, and reliable metadata support matter more than massive scale.

### Where are top-k and top-p used?

Retrieval top-k controls how many chunks are returned. Generation top-k/top-p are LLM sampling controls. This project uses retrieval top-k and low temperature for generation.

### Why is reranking needed?

Reranking improves precision after retrieval. Qdrant quickly finds likely candidates, then the cross-encoder reranker performs a deeper query-vs-chunk relevance check and keeps the best chunks for generation.

### What retriever did you build?

A hybrid retriever using Qdrant with dense semantic embeddings and sparse BM25-style embeddings.

### Why is hybrid better for this data?

Medical insurance documents contain both semantic questions and exact terms like procedure codes, room names, and policy terms. Hybrid retrieval handles both.

### How do you handle metadata filters?

The current app stores metadata but does not expose filters yet. Qdrant supports filtering by payload fields such as source, department, file type, or policy version.

### How do you improve recall without hurting precision?

Use better chunking, hybrid retrieval, query rewriting, slightly higher k, metadata filters, and reranking.

### What happens when the query is vague?

The query rewrite step converts it into a retrieval-optimized query. The generator still answers only from retrieved context.

### Do you rewrite queries?

Yes. The pipeline rewrites the user question before retrieval to improve match quality.

### Do you use multi-query retrieval?

Not currently. It is a future improvement for better recall on broad or ambiguous questions.

### How do you keep answers grounded?

The answer prompt restricts the model to retrieved context and explicitly tells it to say when information is missing.

### What prompt structure did you use?

The prompt defines the assistant role, missing-context behavior, formatting rules, retrieved context, and user question.

### How do you stop invented answers?

Use retrieved context, low temperature, strict prompt instructions, and missing-context fallback. For production, add faithfulness checks and citations.

### How do you format responses for usability?

The prompt asks for plain text, and the backend removes Markdown artifacts before returning the final answer.

## Known Limitations

- No citation rendering in the frontend yet.
- Metadata filters are not exposed through the API yet.
- Evaluation scripts are not yet included.
- Medical safety disclaimers and escalation rules can be improved.
- Local Qdrant locks the database folder, so ingestion should run while the backend is stopped.

## Future Improvements

- Add source citations in answers.
- Add retrieval evaluation with a small golden Q&A set.
- Add metadata filters by department or document type.
- Add streaming responses.
- Add auth for production deployment.
- Add Docker Compose for backend, frontend, and Qdrant server mode.
- Add Markdown rendering in the frontend if richer formatting is desired.
