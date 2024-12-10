import requests
from config import MODEL_BASE_URL
from external.db_service import get_match_data
from external.helper import create_matchup_data, get_h2h_stats


def get_victory_prediction(player_a_id: str, player_b_id: str, lookback: int) -> float:
    (
        player_a_previous_matches,
        player_b_previous_matches,
        _,
        feature_cols,
    ) = get_match_data(player_a_id, player_b_id, lookback)

    player_a_features, player_b_features, player_a_mask, player_b_mask = create_matchup_data(
        player_a_previous_matches, player_b_previous_matches, feature_cols, lookback
    )

    response = requests.post(
        f"{MODEL_BASE_URL}/predict",
        json={
            "X1": player_a_features,
            "X2": player_b_features,
            "M1": player_a_mask,
            "M2": player_b_mask,
        },
    )
    return response.json()["player_a_win_probability"]
