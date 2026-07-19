from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.database import init_db
from app.auth import signup, login
from app.agent.gemini_agent import chat, reset_session
from app.agent.tools import (
    get_balance, list_transactions, get_anomalies,
    get_financial_health_score, list_savings_goals, list_upcoming_bills,
)

app = FastAPI(title="FinPilot AI - Personal Finance Agent", version="1.1")


@app.on_event("startup")
def startup():
    init_db()


# ---------------- Auth ----------------

class SignupRequest(BaseModel):
    email: str
    name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup_endpoint(req: SignupRequest):
    result = signup(req.email, req.name, req.password)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/auth/login")
def login_endpoint(req: LoginRequest):
    result = login(req.email, req.password)
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    return result


# ---------------- Chat ----------------

class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    reply = chat(req.user_id, req.message)
    return ChatResponse(reply=reply)


@app.post("/chat/reset")
def reset_endpoint(user_id: int):
    reset_session(user_id)
    return {"status": "reset", "user_id": user_id}


# ---------------- Data endpoints ----------------

@app.get("/balance")
def balance_endpoint(user_id: int):
    return get_balance(user_id)


@app.get("/transactions")
def transactions_endpoint(user_id: int, category: str = "", limit: int = 20):
    return list_transactions(user_id, category, limit)


@app.get("/anomalies")
def anomalies_endpoint(user_id: int, category: str = ""):
    return get_anomalies(user_id, category)


@app.get("/health-score")
def health_score_endpoint(user_id: int):
    return get_financial_health_score(user_id)


@app.get("/goals")
def goals_endpoint(user_id: int):
    return list_savings_goals(user_id)


@app.get("/bills")
def bills_endpoint(user_id: int):
    return list_upcoming_bills(user_id)


@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}
