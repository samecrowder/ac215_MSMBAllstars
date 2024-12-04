import sys
import os
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch

# Adjust the path to properly import the router module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from chat.router import router  # noqa: E402

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


@patch("chat.router.stream_chat_response")
def test_chat_post_endpoint(mock_stream):
    # Mock the stream response as an async iterator
    mock_stream.return_value = AsyncIterator(["test response"])

    response = client.post(
        "/chat",
        json={
            "player_a_id": "test",
            "player_b_id": "test",
            "query": "test",
            "lookback": 10,
            "history": [],
        },
    )

    assert response.status_code == 200
