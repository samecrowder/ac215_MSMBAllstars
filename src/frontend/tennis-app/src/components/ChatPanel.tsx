import { useState, useEffect, useRef } from "react";

interface Message {
  message: string;
  sender: "user" | "ai";
}

interface ChatPanelProps {
  messages: Message[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [messagesState, setMessages] = useState<Message[]>(messages);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      handleSendMessage(input);
      setInput("");
    }
  };

  const handleSendMessage = async (txt: string) => {
    // Update the messages state with the user's message
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        message: txt,
        sender: "user",
      },
    ]);
    setIsLoading(true);

    try {
      // Call the /chat endpoint with the current messages
      const apiUrl = process.env.REACT_APP_API_URL;
      const response = await fetch(apiUrl + "/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: txt,
          history: messages,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log(data);

      // Update the messages state with the response from the chat endpoint
      setMessages((prevMessages) => [
        ...prevMessages,
        { message: data.message, sender: "ai" },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
    setIsLoading(false);
  };

  // Scroll to the bottom whenever messagesState changes
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
        {/* This div will act as the scroll target */}
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
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
