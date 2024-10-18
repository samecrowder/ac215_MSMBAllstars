import os

from pydantic import BaseModel

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

from typing import List, Optional

import fastapi
from .chat_response import generate_chat_response

app = fastapi.FastAPI()


class ChatResponse(BaseModel):
    response: str


class ChatRequest(BaseModel):
    query: str
    prior_messages: Optional[List[str]] = None


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return {
        "response": generate_chat_response(request.query, request.prior_messages or [])
    }


@app.get("/health")
def health():
    return {"status": "ok"}
