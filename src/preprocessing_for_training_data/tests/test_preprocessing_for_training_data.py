import pytest
import pandas as pd
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper import (  # noqa: E402
    preprocess_data,
    calculate_percentage_difference,
    get_player_last_nplus1_matches,
    get_player_last_nplus1_matches_since_date,
    get_h2h_match_history,
    get_h2h_match_history_since_date,
    get_h2h_stats,
    create_matchup_data,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "tourney_date": pd.to_datetime(
                ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"]
            ),
            "winner_name": ["Player1", "Player2", "Player1", "Player2"],
            "loser_name": ["Player2", "Player3", "Player3", "Player1"],
            "w_stat1": [100, 200, 150, 180],
            "l_stat1": [90, 180, 140, 170],
            "draw_size": [32, 32, 64, 64],
        }
    )


def test_preprocess_data(sample_df):
    player_dfs, feature_cols = preprocess_data(sample_df)

    assert len(player_dfs) == 3  # Player1, Player2, Player3
    assert len(feature_cols) == 2  # w_stat1, l_stat1
    assert "Player1" in player_dfs
    assert "is_winner" in player_dfs["Player1"].columns
    assert "opponent" in player_dfs["Player1"].columns


def test_calculate_percentage_difference():
    assert calculate_percentage_difference(100, 50) == 1.0  # 100% increase
    assert calculate_percentage_difference(50, 100) == -0.5  # 50% decrease
    assert calculate_percentage_difference(100, 0) == 3  # Division by zero case


def test_get_player_last_nplus1_matches(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    matches = get_player_last_nplus1_matches(player_dfs, "Player1", 1)
    assert len(matches) == 2


def test_get_player_last_nplus1_matches_since_date(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    matches = get_player_last_nplus1_matches_since_date(
        player_dfs, "Player1", 2, "2023-01-04"
    )
    assert len(matches) <= 2


def test_get_h2h_match_history(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    h2h = get_h2h_match_history(player_dfs, "Player1", "Player2")
    assert len(h2h) > 0


def test_get_h2h_match_history_since_date(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    h2h = get_h2h_match_history_since_date(
        player_dfs, "Player1", "Player2", "2023-01-04"
    )
    assert isinstance(h2h, pd.DataFrame)


def test_get_h2h_stats(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    h2h = get_h2h_match_history(player_dfs, "Player1", "Player2")
    stats = get_h2h_stats(h2h)
    assert len(stats) == 2
    assert 0 <= stats[0] <= 1  # Win percentage between 0 and 1
    assert isinstance(stats[1], int)  # Total matches is integer


def test_create_matchup_data(sample_df):
    player_dfs, feature_cols = preprocess_data(sample_df)
    p1_history = get_player_last_nplus1_matches(player_dfs, "Player1", 1)
    p2_history = get_player_last_nplus1_matches(player_dfs, "Player2", 1)

    p1_features, p2_features = create_matchup_data(
        p1_history, p2_history, feature_cols, history_len=1
    )

    assert len(p1_features) == 1  # Matches history_len
    assert len(p2_features) == 1
    assert len(p1_features[0]) == len(p2_features[0])  # Same number of features
