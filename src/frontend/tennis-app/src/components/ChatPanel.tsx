import { useCallback, useEffect, useRef, useState } from "react";
import type { Player } from "../players";

const END_MARKER = "**|||END|||**";

interface Message {
  message: string;
  sender: "user" | "assistant";
  pending?: boolean;
}

interface ChatPanelProps {
  initialMessages: Message[];
  matchup: {
    player1: Player;
    player2: Player;
  };
}

export function ChatPanel({ initialMessages, matchup }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [messagesState, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = useCallback(() => {
    const apiUrl = process.env.REACT_APP_API_URL ?? "http://localhost:8000";
    const isOnSecureUrl = apiUrl.startsWith("https://");
    const wsUrl = isOnSecureUrl
      ? apiUrl.replace("https://", "wss://")
      : apiUrl.replace("http://", "ws://");

    const ws = new WebSocket(`${wsUrl}/chat`, isOnSecureUrl ? ["wss"] : []);

    ws.onmessage = (event) => {
      if (event.data === END_MARKER) {
        setMessages((prevMessages) => {
          if (prevMessages.length > 0) {
            return [
              ...prevMessages.slice(0, -1),
              { ...prevMessages[prevMessages.length - 1], pending: false },
            ];
          }
          return prevMessages;
        });
        setIsLoading(false);
      } else {
        setMessages((prevMessages) => {
          if (prevMessages[prevMessages.length - 1]?.sender === "assistant") {
            return [
              ...prevMessages.slice(0, -1),
              {
                message:
                  prevMessages[prevMessages.length - 1].message + event.data,
                sender: "assistant",
                pending: true,
              },
            ];
          } else {
            return [
              ...prevMessages,
              { message: event.data, sender: "assistant", pending: true },
            ];
          }
        });
      }
    };

    ws.onerror = (error) => {
      // eslint-disable-next-line no-console
      console.error("WebSocket error:", error);
      setError(new Error("WebSocket connection error"));
    };

    ws.onclose = (event) => {
      // eslint-disable-next-line no-console
      console.log("WebSocket closed:", event);
      if (!event.wasClean) {
        connectWebSocket(); // Immediate reconnection
      }
    };

    wsRef.current = ws;
    return ws;
  }, []);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      handleSendMessage(input);
      setInput("");
    }
  };

  const handleSendMessage = async (txt: string) => {
    let ws = wsRef.current;

    // If no connection or not open, create new connection
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      ws = connectWebSocket();
      // Wait for connection to open
      await new Promise((resolve) => {
        ws!.onopen = () => resolve(true);
      });
    }

    setMessages((prevMessages) => [
      ...prevMessages,
      {
        message: txt,
        sender: "user",
      },
    ]);
    setIsLoading(true);
    setError(null);

    try {
      ws!.send(
        JSON.stringify({
          query: txt,
          history: messagesState,
          player_a_id: matchup.player1.id,
          player_b_id: matchup.player2.id,
        }),
      );
    } catch (error) {
      setError(error instanceof Error ? error : new Error("Unknown error"));
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messagesState]);

  return (
    <div className="w-96 h-[calc(100vh-4rem)] flex flex-col bg-white rounded-lg border border-gray-300">
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {/* tell user to ask a question */}
        {messagesState.length === 0 && (
          <div className="text-center text-gray-500">
            Ask a question about the match!
          </div>
        )}
        {messagesState.map((message, index) => (
          <div
            key={index}
            data-testid={`${message.sender}-message`}
            data-pending={message.pending}
            className={`p-3 max-w-[80%] rounded-lg relative ${
              message.sender === "user"
                ? "bg-blue-500 text-white ml-auto"
                : "bg-gray-200 text-gray-800 mr-auto"
            }`}
          >
            {message.message}
            {message.sender === "user" && (
              <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-8 border-l-blue-500 border-t-8 border-t-transparent border-b-8 border-b-transparent"></div>
            )}
            {message.sender === "assistant" && (
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-0 h-0 border-r-8 border-r-gray-200 border-t-8 border-t-transparent border-b-8 border-b-transparent"></div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t bg-gray-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button
            type="submit"
            className={`px-4 py-2  text-white rounded-lg  transition-colors ${
              isLoading
                ? "animate-pulse bg-gray-400 cursor-default"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
            disabled={isLoading}
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
        {error && (
          <div role="alert" className="text-red-500">
            {error.message}
          </div>
        )}
      </form>
    </div>
  );
}
