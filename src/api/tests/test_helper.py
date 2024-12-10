import sys
import os
import pandas as pd

# Adjust the path to properly import the helper module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from external.helper import (  # noqa: E402
    preprocess_data,
    calculate_percentage_difference,
    get_player_last_nplus1_matches,
    get_player_last_nplus1_matches_since_date,
    get_h2h_match_history,
    get_h2h_match_history_since_date
)


def test_preprocess_data():
    # Create sample DataFrame
    df = pd.DataFrame(
        {
            "tourney_date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
            "winner_name": ["Player1", "Player2", "Player1"],
            "loser_name": ["Player2", "Player3", "Player3"],
            "w_ace": [10, 8, 12],
            "l_ace": [5, 6, 7],
            "draw_size": [32, 32, 32],
        }
    )

    player_dfs, feature_cols = preprocess_data(df)

    assert len(player_dfs) == 3  # Player1, Player2, Player3
    assert len(feature_cols) == 2  # w_ace, l_ace
    assert "is_winner" in player_dfs["Player1"].columns


def test_calculate_percentage_difference():
    assert calculate_percentage_difference(100, 50) == 1.0
    assert calculate_percentage_difference(50, 100) == -0.5
    assert calculate_percentage_difference(100, 0) == 3  # Test zero division case


def test_get_player_matches():
    df = pd.DataFrame(
        {
            "tourney_date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "winner_name": ["Player1", "Player2"],
            "loser_name": ["Player2", "Player1"],
            "w_ace": [10, 8],
            "l_ace": [5, 6],
            "draw_size": [32, 32],
        }
    )

    player_dfs, _ = preprocess_data(df)

    # Test get_player_last_nplus1_matches
    matches = get_player_last_nplus1_matches(player_dfs, "Player1", 1)
    assert len(matches) > 0

    # Test get_player_last_nplus1_matches_since_date
    matches_since = get_player_last_nplus1_matches_since_date(
        player_dfs, "Player1", 1, "2023-01-02"
    )
    assert isinstance(matches_since, pd.DataFrame)


def test_h2h_functions():
    df = pd.DataFrame(
        {
            "tourney_date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "winner_name": ["Player1", "Player2"],
            "loser_name": ["Player2", "Player1"],
            "w_ace": [10, 8],
            "l_ace": [5, 6],
            "draw_size": [32, 32],
            "is_winner": [1, 0],
        }
    )

    player_dfs, _ = preprocess_data(df)

    # Test h2h match history
    h2h = get_h2h_match_history(player_dfs, "Player1", "Player2")
    assert isinstance(h2h, pd.DataFrame)

    # Test h2h match history since date
    h2h_since = get_h2h_match_history_since_date(
        player_dfs, "Player1", "Player2", "2023-01-02"
    )
    assert isinstance(h2h_since, pd.DataFrame)
