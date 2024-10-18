from typing import List, Optional

from pydantic import BaseModel
import requests

from api.utils import get_and_assert_env_var

service_url = get_and_assert_env_var("LLM_SERVICE_URL")


class RequiresRagResponse(BaseModel):
    requires_rag: bool


def does_request_require_rag(query: str, prior_messages: List[str]) -> bool:
    response = requests.post(
        service_url + "/does_request_require_rag",
        json={"query": query, "prior_messages": prior_messages},
    )
    return RequiresRagResponse(**response.json()).requires_rag


class ChatResponse(BaseModel):
    response: str


def get_chat_response(
    query: str, prior_messages: List[str], rag_results: Optional[List[str]] = None
) -> str:
    response = requests.post(
        service_url + "/chat",
        json={
            "query": query,
            "prior_messages": prior_messages,
            "rag_results": rag_results,
        },
    )

    return ChatResponse(**response.json()).response
