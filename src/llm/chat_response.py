from typing import List

import ollama


def generate_chat_response(query: str, prior_messages: List[str]) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        [
            # TODO change prior_messages to be a list of dicts with role and content
            {"role": "user", "content": message}
            for message in prior_messages
        ],
        {"role": "user", "content": query},
    ]

    response = ollama.chat(
        model="llama3.1",
        messages=messages,
    )
    return response.content.decode("utf-8").strip()
