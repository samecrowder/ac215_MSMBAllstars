import os

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

from typing import List, Optional

import fastapi
from .chat_response import generate_chat_response
from .require_rag import ask_llm_if_rag_is_needed

app = fastapi.FastAPI()


@app.get("/does_request_require_rag")
def does_request_require_rag(query: str, prior_messages: List[str]):
    return {"requires_rag": ask_llm_if_rag_is_needed(query, prior_messages)}


@app.get("/chat")
def chat(
    query: str, prior_messages: List[str], rag_results: Optional[List[str]] = None
):
    return {"response": generate_chat_response(query, prior_messages, rag_results)}


@app.get("/health")
def health():
    return {"status": "ok"}
