from typing import List

from pydantic import BaseModel
import requests
import os

LLM_HOST = os.getenv("LLM_HOST", "llm")
LLM_PORT = os.getenv("LLM_PORT", "8002")


class ChatResponse(BaseModel):
    response: str


def get_chat_response(query, prior_messages):
    url = f"http://{LLM_HOST}:{LLM_PORT}/chat"
    response = requests.post(
        url, json={"query": query, "prior_messages": prior_messages}
    )
    response_data = response.json()
    return response_data["response"]
