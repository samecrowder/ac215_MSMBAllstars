import logging
import os

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

import fastapi
from fastapi.responses import StreamingResponse

from .chat_response import ChatRequest, generate_chat_stream

app = fastapi.FastAPI()


@app.post("/chat")
async def chat(request: ChatRequest):
    logging.info(f"Received chat request: {request}")
    return StreamingResponse(generate_chat_stream(request))


@app.get("/health")
def health():
    return {"status": "ok"}
