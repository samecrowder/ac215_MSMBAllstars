from typing import List

import requests
from pydantic import BaseModel

from api.utils import get_and_assert_env_var

service_url = get_and_assert_env_var("RAG_SERVICE_URL")


class RagResults(BaseModel):
    results: List[str]


def get_rag_results(
    query: str,
    prior_messages: List[str],
) -> List[str]:
    response = requests.post(
        service_url,
        json={
            "query": query,
            "prior_messages": prior_messages,
        },
    )

    return RagResults(**response.json()).results
