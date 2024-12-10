from typing import Any, Dict, List

import numpy as np
import pandas as pd


def preprocess_data(df):

    # Sort by date
    df = df.sort_values("tourney_date")

    # Select relevant features
    feature_cols = [col for col in df.columns if col.startswith("w_") or col.startswith("l_")]

    # Create player-specific dataframes
    player_dfs = {}
    for player in set(df["winner_name"].unique()) | set(df["loser_name"].unique()):
        player_matches = df[(df["winner_name"] == player) | (df["loser_name"] == player)].copy()
        player_matches["is_winner"] = (player_matches["winner_name"] == player).astype(int)
        player_matches["opponent"] = np.where(
            player_matches["winner_name"] == player,
            player_matches["loser_name"],
            player_matches["winner_name"],
        )
        player_matches = player_matches.sort_values("tourney_date").reset_index(drop=True)
        player_dfs[player] = player_matches

    return player_dfs, feature_cols


def calculate_percentage_difference(val1, val2):
    if val2 == 0:
        return 3  # To avoid division by zero, we just give an outsized 300% to val1
    return (val1 - val2) / val2


def get_player_last_nplus1_matches(
    player_dfs: Dict[str, Any], player_id: str, n: int
) -> pd.DataFrame:
    return player_dfs[player_id].tail(n + 1).reset_index()


def get_player_last_nplus1_matches_since_date(
    player_dfs: Dict[str, Any], player_id: str, n: int, date: str
) -> pd.DataFrame:
    return (
        player_dfs[player_id][player_dfs[player_id]["tourney_date"] < date]
        .tail(n + 1)
        .reset_index()
    )


def get_h2h_stats(h2h_df: pd.DataFrame) -> List[float]:
    h2h_wins = h2h_df["is_winner"].sum()
    h2h_total = len(h2h_df)
    h2h_win_percentage = h2h_wins / h2h_total if h2h_total > 0 else 0.5
    return [h2h_win_percentage, h2h_total]


def create_matchup_data(
    p1_history,
    p2_history,
    feature_cols,
    history_len=10,
):
    p1_features, p2_features = [], []
    p1_opponents, p2_opponents = [], []

    for df, features, opponents in [
        (p1_history, p1_features, p1_opponents),
        (p2_history, p2_features, p2_opponents),
    ]:
        for i, matchup in df.iterrows():
            if i == 0:
                continue

            # Store opponent ID for this match
            opponents.append(matchup["opponent"])

            # Extract match features
            match_features = [
                1 if matchup["is_winner"] == 1 else 0,  # player_is_winner
                (
                    df.iloc[i]["tourney_date"] - df.iloc[i - 1]["tourney_date"]
                ).days,  # time_since_last_match
                matchup["draw_size"],  # draw_size
                1 if matchup["surface"] == "clay" else 0,  # surface_clay
                1 if matchup["surface"] == "grass" else 0,  # surface_grass
                1 if matchup["surface"] == "hard" else 0,  # surface_hard
            ]

            # Add player stats and differences
            for col in feature_cols:
                if col.startswith("w_"):
                    player_val = (
                        matchup[col]
                        if matchup["is_winner"] == 1
                        else matchup[col.replace("w_", "l_")]
                    )
                    opponent_val = (
                        matchup[col.replace("w_", "l_")]
                        if matchup["is_winner"] == 1
                        else matchup[col]
                    )
                    diff = calculate_percentage_difference(player_val, opponent_val)
                    match_features.extend([player_val, diff])  # Include raw value and difference
            features.append(match_features)

    # Get player names by counting occurrences in their histories
    p1_names = pd.concat([p1_history["winner_name"], p1_history["loser_name"]])
    p2_names = pd.concat([p2_history["winner_name"], p2_history["loser_name"]])
    p1_name = p1_names.value_counts().index[0]  # Most frequent name is the player
    p2_name = p2_names.value_counts().index[0]

    # Create opponent masks - mark matches where players played each other
    p1_mask = [1 if opp == p2_name else 0 for opp in p1_opponents]
    p2_mask = [1 if opp == p1_name else 0 for opp in p2_opponents]

    return p1_features, p2_features, p1_mask, p2_mask
