import os
import logging

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

from typing import List, Optional

import fastapi
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .chat_response import generate_chat_stream

app = fastapi.FastAPI()


class ChatRequest(BaseModel):
    query: str
    prior_messages: Optional[List[str]] = None


@app.post("/chat")
async def chat(request: ChatRequest):
    logging.info(f"Received chat request: {request}")
    return StreamingResponse(
        generate_chat_stream(request.query, request.prior_messages or [])
    )


@app.get("/health")
def health():
    return {"status": "ok"}
