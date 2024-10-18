import numpy as np


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


def create_matchup_data(
    player1, player2, date, player_dfs, feature_cols, history_len=10
):
    p1_history = (
        player_dfs[player1][player_dfs[player1]["tourney_date"] < date]
        .tail(history_len + 1)
        .reset_index()
    )
    p2_history = (
        player_dfs[player2][player_dfs[player2]["tourney_date"] < date]
        .tail(history_len + 1)
        .reset_index()
    )

    # Includes the 3 features below that are not stats both players have in a match
    num_features = len(feature_cols) + 3

    p1_features = []
    p2_features = []

    for df in [p1_history, p2_history]:
        player_name = player1 if df is p1_history else player2

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

    # Head-to-head history
    h2h = player_dfs[player1][
        (player_dfs[player1]["opponent"] == player2)
        & (player_dfs[player1]["tourney_date"] < date)
    ]
    h2h_wins = h2h["is_winner"].sum()
    h2h_total = len(h2h)
    h2h_win_percentage = h2h_wins / h2h_total if h2h_total > 0 else 0.5

    return p1_features, p2_features, [h2h_win_percentage, h2h_total]
