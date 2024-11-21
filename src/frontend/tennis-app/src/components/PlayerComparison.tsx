import { useCallback, useEffect, useState } from "react";
import { PlayerCard } from "./PlayerCard";
import type { Player } from "../players";

interface PlayerComparisonProps {
  players: Array<Player>;
  matchup: {
    player1: Player;
    player2: Player;
  };
  setMatchup: (matchup: { player1: Player; player2: Player }) => void;
  allowInitialFetch?: boolean;
}

export function PlayerComparison({
  players,
  matchup,
  setMatchup,
  allowInitialFetch = true,
}: PlayerComparisonProps) {
  const [player1WinProbability, setPlayer1WinProbability] = useState<
    number | null
  >(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handlePredictClick = useCallback(
    async (player1Id: string, player2Id: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const apiUrl = process.env.REACT_APP_API_URL;
        const response = await fetch(apiUrl + "/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            player_a_id: player1Id,
            player_b_id: player2Id,
            lookback: 10,
          }),
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await response.json();
        setPlayer1WinProbability(data.player_a_win_probability);
      } catch (error) {
        // log to help test
        console.error("Error fetching prediction:", error);
        setError(error instanceof Error ? error : new Error("Unknown error"));
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (player1WinProbability == null && !isLoading && allowInitialFetch) {
      handlePredictClick(matchup.player1.id, matchup.player2.id);
    }
  }, [
    allowInitialFetch,
    handlePredictClick,
    isLoading,
    matchup,
    player1WinProbability,
  ]);

  return (
    <div className="flex flex-col items-center gap-8">
      <h1 className="text-2xl font-bold">Game-Set-Match</h1>
      <div className="flex items-center gap-16">
        <div className="flex flex-col gap-4">
          <select
            className="p-2 border rounded"
            value={matchup.player1.name}
            onChange={(e) =>
              setMatchup({
                ...matchup,
                player1: players.find((p) => p.name === e.target.value)!,
              })
            }
          >
            {players.map((player) => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
          <PlayerCard
            {...matchup.player1}
            gradientFrom="#4D38C1"
            gradientTo="#271A5B"
          />
        </div>

        <span className="text-4xl font-bold">VS</span>

        <div className="flex flex-col gap-4">
          <select
            className="p-2 border rounded"
            value={matchup.player2.name}
            onChange={(e) =>
              setMatchup({
                ...matchup,
                player2: players.find((p) => p.name === e.target.value)!,
              })
            }
          >
            {players.map((player) => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
          <PlayerCard
            {...matchup.player2}
            gradientFrom="#41C138"
            gradientTo="#325B1A"
          />
        </div>
      </div>

      <button
        onClick={() =>
          handlePredictClick(matchup.player1.id, matchup.player2.id)
        }
        disabled={isLoading}
        className="w-[calc(2*320px+4rem)] bg-gray-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-gray-700 transition-colors"
      >
        {isLoading ? "Loading..." : "Predict Winner"}
      </button>

      {error && <div className="text-red-500">{error.message}</div>}

      {player1WinProbability != null ? (
        <div className="flex items-center w-[calc(2*320px+4rem)] mt-4">
          <span className="text-lg font-bold">
            {(player1WinProbability * 100).toFixed(0)}%
          </span>
          <div className="flex-1 h-4 mx-2 rounded">
            <div
              className="h-full rounded"
              style={{
                width: "100%",
                background: `linear-gradient(to right, #4D38C1 ${
                  player1WinProbability * 100
                }%, #41C138 ${player1WinProbability * 100}%)`,
              }}
            />
          </div>
          <span className="text-lg font-bold">
            {((1 - player1WinProbability) * 100).toFixed(0)}%
          </span>
        </div>
      ) : (
        <div>
          Please select two players then click above to predict the winner.
        </div>
      )}
    </div>
  );
}
