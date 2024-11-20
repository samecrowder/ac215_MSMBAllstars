import logging
import os
from typing import List

import ollama

ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
oc = ollama.Client(host=ollama_host)


def generate_chat_stream(query: str, prior_messages: List[str]):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *[{"role": "user", "content": message} for message in (prior_messages or [])],
        {"role": "user", "content": query},
    ]

    try:
        for chunk in oc.chat(model="llama3.2:1b", messages=messages, stream=True):
            if chunk and chunk.get("message", {}).get("content"):
                content = chunk["message"]["content"]
                yield content
    except Exception as e:
        logging.error(f"Error in generate_chat_stream: {str(e)}", exc_info=True)
        raise
