# model routes

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from api.external.llm_service import does_request_require_rag, get_chat_response
from api.external.rag_service import get_rag_results

router = APIRouter()


class ChatResponse(BaseModel):
    message: str


@router.get("/chat", response_model=ChatResponse)
def chat(query: str, history: Optional[List[ChatResponse]] = None):
    prior_messages = [h.message for h in history or []]
    needs_rag = does_request_require_rag(query, prior_messages)

    if needs_rag:
        rag_results = get_rag_results(query, prior_messages)
    else:
        rag_results = None

    message = get_chat_response(query, prior_messages, rag_results)

    return ChatResponse(message=message)
