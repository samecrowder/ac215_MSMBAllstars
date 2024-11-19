from typing import List

from pydantic import BaseModel
import requests
from ..config import LLM_BASE_URL


class ChatResponse(BaseModel):
    response: str


def get_chat_response(query, prior_messages):
    url = f"{LLM_BASE_URL}/chat"
    response = requests.post(
        url, json={"query": query, "prior_messages": prior_messages}
    )
    response_data = response.json()
    return response_data["response"]
