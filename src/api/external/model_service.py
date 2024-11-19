import os
import requests

from external.db_service import player_dfs, feature_cols
from external.helper import (
    create_matchup_data,
    get_h2h_match_history,
    get_h2h_stats,
    get_player_last_nplus1_matches,
)
from config import MODEL_BASE_URL


def get_victory_prediction(player_a_id: str, player_b_id: str, lookback: int) -> float:
    player_a_previous_matches = get_player_last_nplus1_matches(
        player_dfs, player_a_id, lookback
    )
    player_b_previous_matches = get_player_last_nplus1_matches(
        player_dfs, player_b_id, lookback
    )
    h2h_match_history = get_h2h_match_history(player_dfs, player_a_id, player_b_id)
    h2h_features = get_h2h_stats(h2h_match_history)

    player_a_features, player_b_features = create_matchup_data(
        player_a_previous_matches, player_b_previous_matches, feature_cols, lookback
    )

    response = requests.post(
        f"{MODEL_BASE_URL}/predict",
        json={
            "X1": player_a_features,
            "X2": player_b_features,
            "H2H": [float(x) for x in h2h_features],
        },
    )
    return response.json()["player_a_win_probability"]
