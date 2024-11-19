from typing import List
import os

import ollama


def generate_chat_response(query: str, prior_messages: List[str]) -> str:
    messages: List[ollama.Message] = [
        {"role": "system", "content": "You are a helpful assistant."},
        *[
            # TODO change prior_messages to be a list of dicts with role and content
            {"role": "user", "content": message}
            for message in prior_messages
        ],
        {"role": "user", "content": query},
    ]

    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    oc = ollama.Client(host=ollama_host)
    response = oc.chat(model="llama3.2:1b", messages=messages)

    return response["message"]["content"].strip()
