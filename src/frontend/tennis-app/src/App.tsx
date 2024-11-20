import { useState } from "react";
import { PlayerComparison } from "./components/PlayerComparison";
import { ChatPanel } from "./components/ChatPanel";
import { players } from "./players";

function App() {
  const [messages] = useState<
    Array<{ message: string; sender: "user" | "ai" }>
  >([]);

  return (
    <div className="p-8 flex justify-between">
      <div className="flex flex-col items-center flex-grow">
        <PlayerComparison players={players} />
      </div>
      <ChatPanel messages={messages} />
    </div>
  );
}

export default App;
