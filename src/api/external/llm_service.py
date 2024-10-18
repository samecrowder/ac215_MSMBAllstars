from typing import List

from pydantic import BaseModel
import requests

from api.utils import get_and_assert_env_var

service_url = get_and_assert_env_var("LLM_SERVICE_URL")


class ChatResponse(BaseModel):
    response: str


def get_chat_response(query: str, prior_messages: List[str]) -> str:
    response = requests.post(
        service_url + "/chat",
        json={
            "query": query,
            "prior_messages": prior_messages,
        },
    )

    return ChatResponse(**response.json()).response
