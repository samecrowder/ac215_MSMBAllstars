import { useState } from "react";
import { PlayerCard } from "./PlayerCard";

interface PlayerComparisonProps {
  players: Array<{
    id: string;
    name: string;
    age: number;
    country: string;
    height: string;
    weight: string;
    imageUrl: string;
    gradientFrom: string;
    gradientTo: string;
  }>;
  onPredictClick: () => void;
}

export function PlayerComparison({
  players,
  onPredictClick,
}: PlayerComparisonProps) {
  const [player1, setPlayer1] = useState(players[0]);
  const [player2, setPlayer2] = useState(players[1]);
  const [player1WinProbability, setPlayer1WinProbability] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);

  const handlePredictClick = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player1Id: player1.id,
          player2Id: player2.id,
        }),
      });

      setPlayer1WinProbability(Math.random());

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setPlayer1WinProbability(data.winProbability);
    } catch (error) {
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
          <PlayerCard {...player1} />
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
          <PlayerCard {...player2} />
        </div>
      </div>

      <button
        onClick={handlePredictClick}
        disabled={isLoading}
        className="w-[calc(2*320px+4rem)] bg-gray-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-gray-700 transition-colors"
      >
        {isLoading ? "Loading..." : "Predict Winner"}
      </button>

      <div className="flex items-center w-[calc(2*320px+4rem)] mt-4">
        <span className="text-lg font-bold">
          {(player1WinProbability * 100).toFixed(0)}%
        </span>
        <div className="flex-1 h-4 mx-2 rounded">
          <div
            className="h-full rounded"
            style={{
              width: "100%",
              background: `linear-gradient(to right, red ${
                player1WinProbability * 100
              }%, blue ${player1WinProbability * 100}%)`,
            }}
          />
        </div>
        <span className="text-lg font-bold">
          {((1 - player1WinProbability) * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
