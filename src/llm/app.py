import os

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

from typing import List, Optional

import fastapi
from .chat_response import generate_chat_response

app = fastapi.FastAPI()


@app.get("/chat")
def chat(query: str, prior_messages: List[str]):
    return {"response": generate_chat_response(query, prior_messages)}


@app.get("/health")
def health():
    return {"status": "ok"}
