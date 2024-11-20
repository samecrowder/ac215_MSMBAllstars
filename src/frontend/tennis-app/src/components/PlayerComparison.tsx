import { useState } from "react";
import { PlayerCard } from "./PlayerCard";

interface PlayerComparisonProps {
  players: Array<{
    id: string;
    name: string;
    age: string;
    country: string;
    height: string;
    weight: string;
    imageUrl: string;
  }>;
}

export function PlayerComparison({ players }: PlayerComparisonProps) {
  const [player1, setPlayer1] = useState(players[0]);
  const [player2, setPlayer2] = useState(players[1]);
  const [player1WinProbability, setPlayer1WinProbability] = useState<
    number | null
  >(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handlePredictClick = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.REACT_APP_API_URL;
      console.log(apiUrl);
      const response = await fetch(apiUrl + "/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_a_id: player1.id,
          player_b_id: player2.id,
          lookback: 10,
        }),
      });

      if (!response.ok) {
        console.log(apiUrl, response);
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setPlayer1WinProbability(data.player_a_win_probability);
    } catch (error) {
      setError(error instanceof Error ? error : new Error("Unknown error"));
      console.error("Error fetching prediction:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-8">
      <h1 className="text-2xl font-bold">Game-Set-Match</h1>
      <div className="flex items-center gap-16">
        <div className="flex flex-col gap-4">
          <select
            className="p-2 border rounded"
            value={player1.name}
            onChange={(e) =>
              setPlayer1(players.find((p) => p.name === e.target.value)!)
            }
          >
            {players.map((player) => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
          <PlayerCard
            {...player1}
            gradientFrom="#4D38C1"
            gradientTo="#271A5B"
          />
        </div>

        <span className="text-4xl font-bold">VS</span>

        <div className="flex flex-col gap-4">
          <select
            className="p-2 border rounded"
            value={player2.name}
            onChange={(e) =>
              setPlayer2(players.find((p) => p.name === e.target.value)!)
            }
          >
            {players.map((player) => (
              <option key={player.id} value={player.name}>
                {player.name}
              </option>
            ))}
          </select>
          <PlayerCard
            {...player2}
            gradientFrom="#41C138"
            gradientTo="#325B1A"
          />
        </div>
      </div>

      <button
        onClick={handlePredictClick}
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
