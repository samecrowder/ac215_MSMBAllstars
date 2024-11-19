import { useState } from "react";

interface Message {
  text: string;
  sender: "user" | "ai";
}

interface ChatPanelProps {
  messages: Message[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [messagesState, setMessages] = useState<Message[]>(messages);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      handleSendMessage(input);
      setInput("");
    }
  };

  const handleSendMessage = async (message: string) => {
    // Update the messages state with the user's message
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: message, sender: "user" },
    ]);
    setIsLoading(true);

    try {
      // Call the /chat endpoint with the current messages
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages }), // Pass the current messages
      });

      // temporarily without api endpoint
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "temporary response", sender: "ai" }, // Assuming the response contains a 'reply' field
      ]);

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();

      // Update the messages state with the response from the chat endpoint
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: data.reply, sender: "ai" }, // Assuming the response contains a 'reply' field
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
    setIsLoading(false);
  };

  return (
    <div className="w-96 h-[calc(100vh-4rem)] flex flex-col bg-white rounded-lg border shadow-lg overflow-hidden">
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messagesState.map((message, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg max-w-[80%] ${
              message.sender === "user"
                ? "bg-blue-500 text-white ml-auto"
                : "bg-gray-200 text-gray-800 mr-auto"
            }`}
          >
            {message.text}
          </div>
        ))}
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
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
