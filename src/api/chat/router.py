# model routes

import json
import logging
import os

from external.llm_service import ChatRequest, stream_chat_response
from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

router = APIRouter()


END_MARKER = "**|||END|||**"


@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    if os.getenv("ENV") == "prod":
        await websocket.accept(subprotocol="wss")
    else:
        await websocket.accept()

    logging.info("WebSocket connection accepted")
    try:
        while True:
            text_data = await websocket.receive_text()
            logging.info(f"Received WebSocket message: {text_data}")
            request = ChatRequest(**json.loads(text_data))

            async for chunk in stream_chat_response(request):
                await websocket.send_text(chunk)

            await websocket.send_text(END_MARKER)
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        raise
    finally:
        await websocket.close()


class ChatResponse(BaseModel):
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # run chat stream and append to a string, then return the string
    response = ""
    async for chunk in stream_chat_response(request):
        response += chunk
    return ChatResponse(message=response)
