import logging
from typing import List

import httpx
from config import LLM_BASE_URL
from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str


async def stream_chat_response(query: str, prior_messages: List[str]):
    url = f"{LLM_BASE_URL}/chat"
    
    async with httpx.AsyncClient() as client:
        logging.info(f"Sending request to {url}")
        async with client.stream(
            'POST',
            url,
            json={"query": query, "prior_messages": prior_messages},
            timeout=None
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
