import logging
from typing import List, Literal

import httpx
from external.db_service import get_match_data
from config import LLM_BASE_URL
from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str
    sender: Literal["user", "assistant"]

    class Config:
        extra = "allow"


class ChatRequest(BaseModel):
    player_a_id: str
    player_b_id: str
    lookback: int = 10

    query: str
    history: List[ChatMessage] = []  # Default to empty list if not provided


def make_rag_system_message_from_match_data(
    player_a_name: str, player_b_name: str, lookback: int
) -> str:
    (
        player_a_previous_matches,
        player_b_previous_matches,
        h2h_match_history,
        _feature_cols,
    ) = get_match_data(player_a_name, player_b_name, lookback)

    # Format player A's recent matches
    player_a_stats = "\nPlayer A ({}) recent matches:\n".format(player_a_name)
    for _, match in player_a_previous_matches.iterrows():
        player_a_stats += (
            f"- {match['tourney_name']} ({match['surface']}) vs {match['opponent']}: "
            f"{'Won' if match['is_winner'] else 'Lost'} "
            f"| Score: {match['score']} "
            f"| Round: {match['round']}\n"
        )

    # Format player B's recent matches
    player_b_stats = "\nPlayer B ({}) recent matches:\n".format(player_b_name)
    for _, match in player_b_previous_matches.iterrows():
        player_b_stats += (
            f"- {match['tourney_name']} ({match['surface']}) vs {match['opponent']}: "
            f"{'Won' if match['is_winner'] else 'Lost'} "
            f"| Score: {match['score']} "
            f"| Round: {match['round']}\n"
        )

    # Format head-to-head history, which are from the perspective of player A
    h2h_stats = "\nHead-to-head history:\n"
    if len(h2h_match_history) > 0:
        for _, match in h2h_match_history.iterrows():
            winner = player_a_name if match["is_winner"] else player_b_name
            h2h_stats += (
                f"- {match['tourney_name']} ({match['surface']}): "
                f"{winner} won "
                f"| Score: {match['score']} "
                f"| Round: {match['round']}\n"
            )
    else:
        h2h_stats += f"No head-to-head matches found for {player_a_name} and {player_b_name}.\n"

    # Combine all information
    return f"""Selected Matchup: {player_a_name} vs {player_b_name}.
Here is the relevant match data for the last {lookback} matches:

{player_a_stats}
{player_b_stats}
{h2h_stats}

Please use this historical match data to inform your responses about the players and their potential
matchup. Consider factors like recent form, surface performance, and head-to-head record in your
analysis.
"""


async def stream_chat_response(request: ChatRequest):
    url = f"{LLM_BASE_URL}/chat"

    rag_match_data_message = make_rag_system_message_from_match_data(
        request.player_a_id, request.player_b_id, request.lookback
    )

    async with httpx.AsyncClient() as client:
        logging.info(f"Sending request to {url}")
        async with client.stream(
            "POST",
            url,
            json={
                "query": request.query,
                "history": [
                    {"message": message.message, "sender": message.sender}
                    for message in request.history
                ],
                "rag_system_message": rag_match_data_message,
            },
            timeout=None,
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
