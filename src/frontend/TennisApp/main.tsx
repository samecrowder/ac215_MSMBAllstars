"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

const names = ["Alice", "Bob", "Charlie", "David", "Eve"];

export default function TwoPanelChat() {
  const [selectedName1, setSelectedName1] = useState(names[0]);
  const [selectedName2, setSelectedName2] = useState(names[1]);
  const [messages, setMessages] = useState([
    { sender: "Alice", content: "Hello there!" },
    { sender: "Bob", content: "Hi Alice, how are you?" },
  ]);
  const [inputMessage, setInputMessage] = useState("");

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setMessages([
        ...messages,
        { sender: selectedName1, content: inputMessage.trim() },
      ]);
      setInputMessage("");
    }
  };

  return (
    <div className="flex h-screen p-4 gap-6">
      {/* Left Panel */}
      <div className="w-1/2 flex flex-col justify-start gap-4">
        <Card className="w-full">
          <CardContent className="p-4 flex flex-col items-center gap-2">
            <Select value={selectedName1} onValueChange={setSelectedName1}>
              <SelectTrigger className="w-full mb-4">
                <SelectValue>{selectedName1}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {names.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <CardTitle className="text-lg">{selectedName1}</CardTitle>
          </CardContent>
        </Card>
        <Card className="w-full">
          <CardContent className="p-4 flex flex-col items-center gap-2">
            <Select value={selectedName2} onValueChange={setSelectedName2}>
              <SelectTrigger className="w-full mb-4">
                <SelectValue>{selectedName2}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {names.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <CardTitle className="text-lg">{selectedName2}</CardTitle>
          </CardContent>
        </Card>
      </div>

      {/* Right Panel */}
      <div className="w-1/2 flex flex-col items-center">
        <div className="w-full max-w-md h-full">
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle>Chat</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col">
              <ScrollArea className="flex-grow mb-4 p-4 border rounded">
                {messages.map((message, index) => (
                  <div key={index} className="mb-2">
                    <span className="font-bold">{message.sender}: </span>
                    {message.content}
                  </div>
                ))}
              </ScrollArea>
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                />
                <Button onClick={handleSendMessage}>Send</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
