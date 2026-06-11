from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import MedibudiRAG
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI(title="Medibudi RAG API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG on startup (or lazy load)
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    global rag_pipeline
    try:
        rag_pipeline = MedibudiRAG()
        print("Medibudi RAG Pipeline initialized successfully.")
    except Exception as e:
        print(f"Warning: RAG Pipeline initialization failed. Did you run ingest.py? Error: {e}")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
async def serve_frontend():
    # Serve the frontend HTML file
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Medibudi RAG API</h1><p>index.html not found.</p>")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG Pipeline not initialized. Check server logs.")
    try:
        reply = rag_pipeline.ask(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
