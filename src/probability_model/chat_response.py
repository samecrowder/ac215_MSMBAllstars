from typing import List

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

    oc = ollama.Client(host="http://ollama:11434")
    response = oc.chat(model="llama3.2:1b", messages=messages)

    return response['message']['content'].strip()
