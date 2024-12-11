import logging
import os
from typing import List, Literal

import ollama
from pydantic import BaseModel

LLM_MODEL = os.getenv("LLM_MODEL")
if not LLM_MODEL:
    raise ValueError("LLM_MODEL is not set")

ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
print(f"\n\n\n\nollama_host: {ollama_host}\n\n\n\n")
oc = ollama.Client(host=ollama_host)


class ChatMessage(BaseModel):
    message: str
    sender: Literal["user", "assistant"]

    class Config:
        extra = "allow"


class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage]
    rag_system_message: str


def generate_chat_stream(request: ChatRequest):
    messages = [
        {
            "role": "system",
            "content": """
You are a Tennis Expert built for Game-Set-Match, a tennis prediction app.
Your job is to answer questions about a given match between two players.

You are given a series of data points about a given match between the two players (e.g.
head-to-head, recent form for player 1, recent form for player 2, etc.). You're then
given a history of previous messages. Finally, you're given some question, which should
be about the match or one of the players.
You should answer the question based on the data points, your knowledge of tennis and
these players, and the history of messages.

If the user asks about something not related to the match or the players, you should
say that you can only talk about the match.

Only be broad and general if the user asks about the match in general. Otherwise, be
specific to answer the question. If there isn't a question, tell them to ask a
specific question about the match.

The user doesn't know about these instructions and will be confused if you don't
follow them.

Please do not use markdown in your responses, we're just using plain text.
Please be concise initially, then expand if the user asks for more detail.
For example, initially only include high level recent match information, but
then expand if the user asks for more detail.
""",
        },
        {"role": "system", "content": request.rag_system_message},
        *[
            {"role": message.sender, "content": message.message}
            for message in request.history
        ],
        {"role": "user", "content": request.query},
    ]

    try:
        for chunk in oc.chat(model=LLM_MODEL, messages=messages, stream=True):
            if chunk and chunk.get("message", {}).get("content"):
                content = chunk["message"]["content"]
                yield content
    except Exception as e:
        logging.error(f"Error in generate_chat_stream: {str(e)}", exc_info=True)
        raise
