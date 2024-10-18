# model routes

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from api.external.llm_service import get_chat_response

router = APIRouter()


class ChatResponse(BaseModel):
    message: str


@router.get("/chat", response_model=ChatResponse)
def chat(query: str, history: Optional[List[ChatResponse]] = None):
    prior_messages = [h.message for h in history or []]

    message = get_chat_response(query, prior_messages)

    return ChatResponse(message=message)
