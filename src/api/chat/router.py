# model routes

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from external.llm_service import get_chat_response

router = APIRouter()


class ChatMessage(BaseModel):
    message: str


class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []  # Default to empty list if not provided


class ChatResponse(BaseModel):
    message: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    prior_messages = [h.message for h in request.history]
    message = get_chat_response(request.query, prior_messages)
    return ChatResponse(message=message)
