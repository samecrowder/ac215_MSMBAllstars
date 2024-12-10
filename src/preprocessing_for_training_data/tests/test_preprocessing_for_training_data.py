import pytest
import pandas as pd
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper import (  # noqa: E402
    preprocess_data,
    calculate_percentage_difference,
    get_player_last_nplus1_matches_since_date,
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
            "surface": ["hard", "clay", "grass", "hard"],  # Added surface
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


def test_get_player_last_nplus1_matches_since_date(sample_df):
    player_dfs, _ = preprocess_data(sample_df)
    matches = get_player_last_nplus1_matches_since_date(player_dfs, "Player1", 2, "2023-01-04")
    assert len(matches) <= 2


def test_create_matchup_data(sample_df):
    player_dfs, feature_cols = preprocess_data(sample_df)
    p1_history = get_player_last_nplus1_matches_since_date(player_dfs, "Player1", 2, "2023-01-04")
    p2_history = get_player_last_nplus1_matches_since_date(player_dfs, "Player2", 2, "2023-01-04")

    p1_features, p2_features, p1_mask, p2_mask = create_matchup_data(
        p1_history, p2_history, feature_cols, history_len=1
    )

    # Test features
    assert isinstance(p1_features, list)
    assert isinstance(p2_features, list)
    assert len(p1_features) <= 1  # Matches history_len
    assert len(p2_features) <= 1
    if len(p1_features) > 0 and len(p2_features) > 0:
        assert len(p1_features[0]) == len(p2_features[0])  # Same number of features

    # Test masks
    assert isinstance(p1_mask, list)
    assert isinstance(p2_mask, list)
    assert len(p1_mask) == len(p1_features)
    assert len(p2_mask) == len(p2_features)
    assert all(isinstance(x, int) and x in [0, 1] for x in p1_mask)
    assert all(isinstance(x, int) and x in [0, 1] for x in p2_mask)


def test_data_preprocessing_pipeline(sample_df):
    """Test the core data processing pipeline without GCS dependencies"""
    from preprocess import LOOKBACK
    from helper import (
        create_matchup_data,
        get_player_last_nplus1_matches_since_date,
        preprocess_data,
    )

    # Convert date column to datetime
    sample_df["tourney_date"] = pd.to_datetime(sample_df["tourney_date"])

    # Process the sample data
    player_dfs, feature_cols = preprocess_data(sample_df)

    # Test data transformation for one matchup
    # Use the last match (2023-01-04) to ensure we have some history
    matchup = sample_df.iloc[-1]  # Changed from iloc[0] to iloc[-1]
    winner = matchup["winner_name"]  # Player2
    loser = matchup["loser_name"]  # Player1
    date = matchup["tourney_date"]  # 2023-01-04

    # Get player histories
    winner_history = get_player_last_nplus1_matches_since_date(player_dfs, winner, LOOKBACK, date)
    loser_history = get_player_last_nplus1_matches_since_date(player_dfs, loser, LOOKBACK, date)

    # Create matchup features with opponent masks
    winner_features, loser_features, winner_mask, loser_mask = create_matchup_data(
        winner_history, loser_history, feature_cols, LOOKBACK
    )

    # Assertions
    assert isinstance(winner_features, list)
    assert isinstance(loser_features, list)
    assert isinstance(winner_mask, list)
    assert isinstance(loser_mask, list)
    assert len(winner_features) <= LOOKBACK  # Can be less than LOOKBACK if not enough history
    assert len(loser_features) <= LOOKBACK
    assert len(winner_mask) == len(winner_features)
    assert len(loser_mask) == len(loser_features)
    if len(winner_features) > 0:
        assert all(isinstance(x, (int, float)) for x in winner_features[0])  # Check feature types
    if len(loser_features) > 0:
        assert all(isinstance(x, (int, float)) for x in loser_features[0])
