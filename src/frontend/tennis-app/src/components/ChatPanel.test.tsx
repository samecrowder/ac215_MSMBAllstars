import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatPanel } from "./ChatPanel";
import type { Player } from "../players";

describe("ChatPanel", () => {
  let mockWebSocket: any;

  const mockMessages = [
    { message: "Hello", sender: "user" as const },
    { message: "Hi there!", sender: "assistant" as const },
  ];

  const mockMatchup: {
    player1: Player;
    player2: Player;
  } = {
    player1: {
      id: "roger-federer",
      name: "Roger Federer",
      age: "42",
      country: "Switzerland",
      height: "6'1\"",
      weight: "187 lbs",
      imageUrl: "https://example.com/federer.jpg",
    },
    player2: {
      id: "carlos-alcaraz",
      name: "Carlos Alcaraz",
      age: "21",
      country: "Spain",
      height: "6'0\"",
      weight: "163 lbs",
      imageUrl: "/images/carlos_alcaraz.png",
    },
  };

  beforeEach(() => {
    // Mock scrollIntoView
    Element.prototype.scrollIntoView = jest.fn();

    // Mock WebSocket
    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
      onmessage: jest.fn(),
    };
    // @ts-ignore
    global.WebSocket = jest.fn().mockImplementation(() => mockWebSocket);
  });

  test("renders chat messages", () => {
    render(<ChatPanel initialMessages={mockMessages} matchup={mockMatchup} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
  });

  test("renders input field and send button", () => {
    render(<ChatPanel initialMessages={[]} matchup={mockMatchup} />);
    expect(
      screen.getByPlaceholderText("Type your message..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Send")).toBeInTheDocument();
  });

  test("allows user to type message", async () => {
    render(<ChatPanel initialMessages={[]} matchup={mockMatchup} />);
    const input = screen.getByPlaceholderText(
      "Type your message...",
    ) as HTMLInputElement;
    await userEvent.type(input, "New message");
    expect(input.value).toBe("New message");
  });

  test("clears input after sending message", async () => {
    render(<ChatPanel initialMessages={[]} matchup={mockMatchup} />);
    const input = screen.getByPlaceholderText(
      "Type your message...",
    ) as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(input.value).toBe("");
  });

  test("disables input while loading", async () => {
    render(<ChatPanel initialMessages={[]} matchup={mockMatchup} />);
    const input = screen.getByPlaceholderText(
      "Type your message...",
    ) as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(input).toBeDisabled();
  });

  test("sends message through WebSocket", async () => {
    render(<ChatPanel initialMessages={[]} matchup={mockMatchup} />);
    const input = screen.getByPlaceholderText(
      "Type your message...",
    ) as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(mockWebSocket.send).toHaveBeenCalledWith(
      expect.stringContaining('"query":"New message"')
    );
    expect(mockWebSocket.send).toHaveBeenCalledWith(
      expect.stringContaining('"player_a_id":"roger-federer"')
    );
    expect(mockWebSocket.send).toHaveBeenCalledWith(
      expect.stringContaining('"player_b_id":"carlos-alcaraz"')
    );
  });
});
