from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from app.core.rbac import DEMO_USERS, SQL_RAG_ROLES, collections_for_role, is_valid_role
from app.sql_rag import should_use_sql_rag

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str
    collections: list[str]


class ChatRequest(BaseModel):
    message: str | None = None
    question: str | None = None


class ChatResponse(BaseModel):
    answer: str
    reply: str
    sources: list[dict] = []
    retrieval_type: str
    role: str
    collections: list[str]


class CollectionsResponse(BaseModel):
    role: str
    collections: list[str]
    demo_users: list[dict[str, str]]


def _session_from_header(request: Request, authorization: str | None) -> dict[str, str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Login required. Select a demo user role first.")

    token = authorization.split(" ", 1)[1].strip()
    session = request.app.state.sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session token.")
    return session


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request):
    session = request.app.state.sessions.login(body.username, body.password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid demo username or password.")

    return LoginResponse(
        token=session["token"],
        username=session["username"],
        role=session["role"],
        collections=collections_for_role(session["role"]),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request_body: ChatRequest,
    request: Request,
    authorization: str | None = Header(default=None),
):
    rag_pipeline = request.app.state.rag_pipeline
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG Pipeline not initialized. Check server logs.")

    session = _session_from_header(request, authorization)
    role = session["role"]
    question = (request_body.question or request_body.message or "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question is required.")

    try:
        if should_use_sql_rag(question):
            if role not in SQL_RAG_ROLES:
                answer = (
                    "This looks like a database or operational analytics question. "
                    "Your current role does not have SQL RAG access. Please use an admin "
                    "or billing executive demo user for claims and maintenance-ticket queries."
                )
                return ChatResponse(
                    answer=answer,
                    reply=answer,
                    sources=[],
                    retrieval_type="blocked_by_rbac",
                    role=role,
                    collections=collections_for_role(role),
                )

            sql_result = request.app.state.sql_rag.ask(question)
            answer = str(sql_result["answer"])
            return ChatResponse(
                answer=answer,
                reply=answer,
                sources=sql_result.get("sources", []),
                retrieval_type="sql_rag",
                role=role,
                collections=collections_for_role(role),
            )

        result = rag_pipeline.ask_with_role(question, role)
        answer = str(result["answer"])
        return ChatResponse(
            answer=answer,
            reply=answer,
            sources=result.get("sources", []),
            retrieval_type=str(result["retrieval_type"]),
            role=role,
            collections=collections_for_role(role),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/collections/{role}", response_model=CollectionsResponse)
async def collections(role: str):
    if not is_valid_role(role):
        raise HTTPException(status_code=404, detail=f"Unknown role: {role}")

    demo_users = [
        {"username": username, "role": user["role"]}
        for username, user in DEMO_USERS.items()
    ]
    return CollectionsResponse(
        role=role,
        collections=collections_for_role(role),
        demo_users=demo_users,
    )
