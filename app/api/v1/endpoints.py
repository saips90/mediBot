from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request_body: ChatRequest, request: Request):
    rag_pipeline = request.app.state.rag_pipeline
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG Pipeline not initialized. Check server logs.")

    try:
        reply = rag_pipeline.ask(request_body.message)
        return ChatResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
