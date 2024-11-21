import { useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { PlayerComparison } from "./components/PlayerComparison";
import { type Player, players } from "./players";

function App() {
  const [matchup, setMatchup] = useState<{
    player1: Player;
    player2: Player;
  }>({
    player1: players[0],
    player2: players[1],
  });

  return (
    <div className="p-8 flex justify-between">
      <div className="flex flex-col items-center flex-grow">
        <PlayerComparison
          matchup={matchup}
          setMatchup={setMatchup}
          players={players}
        />
      </div>
      <ChatPanel initialMessages={[]} matchup={matchup} />
    </div>
  );
}

export default App;
