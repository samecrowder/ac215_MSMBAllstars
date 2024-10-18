from typing import List

import ollama


def ask_llm_if_rag_is_needed(query: str, prior_messages: List[str]) -> bool:
    response = ollama.generate(
        model="llama3.1",
        prompt=f"""
Do we need to use RAG for this query: {query}? 
Prior messages: {prior_messages}. 
Only respond with "True" or "False". If you respond with anything else, the program will crash.
""",
    )
    return response.content.decode("utf-8").strip() == "True"
