from typing import Any, Dict, List

import numpy as np
import pandas as pd


def preprocess_data(df):

    # Sort by date
    df = df.sort_values("tourney_date")

    # Select relevant features
    feature_cols = [
        col for col in df.columns if col.startswith("w_") or col.startswith("l_")
    ]

    # Create player-specific dataframes
    player_dfs = {}
    for player in set(df["winner_name"].unique()) | set(df["loser_name"].unique()):
        player_matches = df[
            (df["winner_name"] == player) | (df["loser_name"] == player)
        ].copy()
        player_matches["is_winner"] = (player_matches["winner_name"] == player).astype(
            int
        )
        player_matches["opponent"] = np.where(
            player_matches["winner_name"] == player,
            player_matches["loser_name"],
            player_matches["winner_name"],
        )
        player_dfs[player] = player_matches.reset_index()

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


def get_h2h_match_history(
    player_dfs: Dict[str, Any], player_a_id: str, player_b_id: str
) -> pd.DataFrame:
    return player_dfs[player_a_id][player_dfs[player_a_id]["opponent"] == player_b_id]


def get_h2h_match_history_since_date(
    player_dfs: Dict[str, Any], player_a_id: str, player_b_id: str, date: str
) -> pd.DataFrame:
    return player_dfs[player_a_id][
        (player_dfs[player_a_id]["opponent"] == player_b_id)
        & (player_dfs[player_a_id]["tourney_date"] < date)
    ]


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
    # Includes the 3 features below that are not stats both players have in a match
    num_features = len(feature_cols) + 3

    p1_features = []
    p2_features = []

    for df in [p1_history, p2_history]:
        player_features = []
        for i, matchup in df.iterrows():
            if i == 0:
                continue

            # TODO: Surface Indicator, one of Hard, Clay, Grass, Carpet
            player_is_winner = 1 if matchup["is_winner"] == 1 else 0
            time_since_last_match = (
                df.iloc[i]["tourney_date"] - df.iloc[i - 1]["tourney_date"]
            ).days
            draw_size = matchup["draw_size"]

            match_features = [player_is_winner, time_since_last_match, draw_size]
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
                    match_features.extend(
                        [player_val, diff]
                    )  # Include raw value and difference
            player_features.append(match_features)

        if len(player_features) < history_len:
            padding = [[0] * num_features] * (history_len - len(player_features))
            player_features = padding + player_features

        if df is p1_history:
            p1_features = player_features
        else:
            p2_features = player_features

    return p1_features, p2_features
