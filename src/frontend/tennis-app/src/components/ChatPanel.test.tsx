import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatPanel } from "./ChatPanel";

describe("ChatPanel", () => {
  let mockWebSocket: any;

  const mockMessages = [
    { message: "Hello", sender: "user" as const },
    { message: "Hi there!", sender: "ai" as const },
  ];

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
    render(<ChatPanel messages={mockMessages} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
  });

  test("renders input field and send button", () => {
    render(<ChatPanel messages={[]} />);
    expect(
      screen.getByPlaceholderText("Type your message...")
    ).toBeInTheDocument();
    expect(screen.getByText("Send")).toBeInTheDocument();
  });

  test("allows user to type message", async () => {
    render(<ChatPanel messages={[]} />);
    const input = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLInputElement;
    await userEvent.type(input, "New message");
    expect(input.value).toBe("New message");
  });

  test("clears input after sending message", async () => {
    render(<ChatPanel messages={[]} />);
    const input = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(input.value).toBe("");
  });

  test("disables input while loading", async () => {
    render(<ChatPanel messages={[]} />);
    const input = screen.getByPlaceholderText(
      "Type your message..."
    ) as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(input).toBeDisabled();
  });

  test("sends message through WebSocket", async () => {
    render(<ChatPanel messages={[]} />);
    const input = screen.getByPlaceholderText("Type your message...") as HTMLInputElement;
    const sendButton = screen.getByText("Send");

    await userEvent.type(input, "New message");
    fireEvent.click(sendButton);

    expect(mockWebSocket.send).toHaveBeenCalledWith(
      expect.stringContaining("New message")
    );
  });
});
