import { useState } from "react";
import { PlayerComparison } from "./components/PlayerComparison";
import { ChatPanel } from "./components/ChatPanel";
import { players } from "./players";

function App() {
  const [messages, setMessages] = useState<
    Array<{ text: string; sender: "user" | "ai" }>
  >([]);

  const handlePredictClick = () => {
    // Handle prediction logic here
  };

  return (
    <div className="p-8 flex justify-between">
      <div className="flex flex-col items-center flex-grow">
        <PlayerComparison
          players={players}
          onPredictClick={handlePredictClick}
        />
      </div>
      <ChatPanel messages={messages} />
    </div>
  );
}

export default App;
