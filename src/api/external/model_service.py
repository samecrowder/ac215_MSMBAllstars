import requests

from ..external.db_service import (
    get_head_to_head_match_history,
    get_player_last_nplus1_matches,
)
from ..utils import get_and_assert_env_var

service_url = get_and_assert_env_var("MODEL_SERVICE_URL")


def get_victory_prediction(player_a_id: str, player_b_id: str, lookback: int) -> float:
    player_a_previous_matches = get_player_last_nplus1_matches(player_a_id, lookback)
    player_b_previous_matches = get_player_last_nplus1_matches(player_b_id, lookback)
    head_to_head_match_history = get_head_to_head_match_history(
        player_a_id, player_b_id
    )

    response = requests.post(
        service_url,
        json={
            "player_a_previous_matches": player_a_previous_matches,
            "player_b_previous_matches": player_b_previous_matches,
            "head_to_head_match_history": head_to_head_match_history,
        },
    )
    return response.json()["player_a_win_probability"]
