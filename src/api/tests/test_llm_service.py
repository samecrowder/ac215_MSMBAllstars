import pandas as pd
from external.llm_service import make_rag_system_message_from_match_data
from unittest.mock import patch


def test_make_rag_system_message():
    # Mock data
    player_a_matches = pd.DataFrame(
        {
            "tourney_name": ["Wimbledon"],
            "surface": ["Grass"],
            "opponent": ["Player C"],
            "is_winner": [True],
            "score": ["6-4 6-4"],
            "round": ["F"],
        }
    )

    player_b_matches = pd.DataFrame(
        {
            "tourney_name": ["US Open"],
            "surface": ["Hard"],
            "opponent": ["Player D"],
            "is_winner": [False],
            "score": ["3-6 4-6"],
            "round": ["SF"],
        }
    )

    h2h_matches = pd.DataFrame(
        {
            "tourney_name": ["Australian Open"],
            "surface": ["Hard"],
            "is_winner": [True],
            "score": ["7-6 6-4"],
            "round": ["QF"],
        }
    )

    # Mock the get_match_data function
    with patch("external.llm_service.get_match_data") as mock_get_data:
        mock_get_data.return_value = (
            player_a_matches,
            player_b_matches,
            h2h_matches,
            None,  # feature_cols not used in the function
        )

        # Call the function
        result = make_rag_system_message_from_match_data(
            "Player A", "Player B", lookback=10
        )

        # Basic assertions
        assert "Player A vs Player B" in result
        assert "Wimbledon (Grass) vs Player C: Won" in result
        assert "US Open (Hard) vs Player D: Lost" in result
        assert "Australian Open (Hard): Player A won" in result
        assert "last 10 matches" in result


def test_make_rag_system_message_no_h2h():
    # Mock data
    player_a_matches = pd.DataFrame(
        {
            "tourney_name": ["Wimbledon"],
            "surface": ["Grass"],
            "opponent": ["Player C"],
            "is_winner": [True],
            "score": ["6-4 6-4"],
            "round": ["F"],
        }
    )

    player_b_matches = pd.DataFrame(
        {
            "tourney_name": ["US Open"],
            "surface": ["Hard"],
            "opponent": ["Player D"],
            "is_winner": [False],
            "score": ["3-6 4-6"],
            "round": ["SF"],
        }
    )

    # Empty DataFrame for no head-to-head matches
    h2h_matches = pd.DataFrame(
        columns=["tourney_name", "surface", "is_winner", "score", "round"]
    )

    # Mock the get_match_data function
    with patch("external.llm_service.get_match_data") as mock_get_data:
        mock_get_data.return_value = (
            player_a_matches,
            player_b_matches,
            h2h_matches,
            None,  # feature_cols not used in the function
        )

        # Call the function
        result = make_rag_system_message_from_match_data(
            "Player A", "Player B", lookback=10
        )

        # Basic assertions
        assert "Player A vs Player B" in result
        assert "Wimbledon (Grass) vs Player C: Won" in result
        assert "US Open (Hard) vs Player D: Lost" in result
        assert "No head-to-head matches found for Player A and Player B" in result
