import requests

from ..external.db_service import (
    get_head_to_head_match_history,
    get_player_last_n_matches,
)
from ..utils import get_and_assert_env_var

service_url = get_and_assert_env_var("MODEL_SERVICE_URL")


def get_victory_prediction(player_a_id: str, player_b_id: str) -> float:
    player_a_last_10_matches = get_player_last_n_matches(player_a_id, 10)
    player_b_last_10_matches = get_player_last_n_matches(player_b_id, 10)
    head_to_head_match_history = get_head_to_head_match_history(
        player_a_id, player_b_id
    )

    response = requests.post(
        service_url,
        json={
            "player_a_last_10_matches": player_a_last_10_matches,
            "player_b_last_10_matches": player_b_last_10_matches,
            "head_to_head_match_history": head_to_head_match_history,
        },
    )
    return response.json()["player_a_win_probability"]
