import { useState, useEffect, useRef } from "react";

const END_MARKER = "**|||END|||**";

interface Message {
  message: string;
  sender: "user" | "ai";
  pending?: boolean;
}

interface ChatPanelProps {
  messages: Message[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [messagesState, setMessages] = useState<Message[]>(messages);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // init ws connection
    const apiUrl = process.env.REACT_APP_API_URL ?? "http://localhost:8000";
    const wsUrl = apiUrl.startsWith("https://")
      ? apiUrl.replace("https://", "wss://")
      : apiUrl.replace("http://", "ws://");
    const ws = new WebSocket(`${wsUrl}/chat`);
    ws.onmessage = (event) => {
      if (event.data === END_MARKER) {
        // set the last message to not pending
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
          if (prevMessages[prevMessages.length - 1]?.sender === "ai") {
            return [
              // remove the last pending message
              ...prevMessages.slice(0, -1),
              // add the new message
              {
                message:
                  prevMessages[prevMessages.length - 1].message + event.data,
                sender: "ai",
                pending: true,
              },
            ];
          } else {
            return [
              ...prevMessages,
              { message: event.data, sender: "ai", pending: true },
            ];
          }
        });
      }
    };
    wsRef.current = ws;

    return () => {
      // Cleanup WebSocket connection on component unmount
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      handleSendMessage(input);
      setInput("");
    }
  };

  const handleSendMessage = async (txt: string) => {
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
      if (!wsRef.current) {
        throw new Error("WebSocket connection not established");
      }

      wsRef.current?.send(
        JSON.stringify({
          query: txt,
          history: messagesState,
        })
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
            {message.sender === "ai" && (
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
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            disabled={isLoading}
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
        {error && <div className="text-red-500">{error.message}</div>}
      </form>
    </div>
  );
}
