import { render, screen } from "@testing-library/react";
import React from "react";
import App from "./App";
import { players } from "./players";

describe("App", () => {
  beforeEach(() => {
    // Mock scrollIntoView
    Element.prototype.scrollIntoView = jest.fn();
  });

  test("renders Game-Set-Match", () => {
    render(<App />);
    const linkElement = screen.getByText(/Game-Set-Match/i);
    expect(linkElement).toBeInTheDocument();
  });

  test("renders PlayerComparison component with correct initial players", () => {
    render(<App />);
    // Check player cards by their unique heading elements
    const player1Card = screen.getAllByRole("heading", { level: 1 }).find(h => h.textContent === players[0].name);
    const player2Card = screen.getAllByRole("heading", { level: 1 }).find(h => h.textContent === players[1].name);
    expect(player1Card).toBeInTheDocument();
    expect(player2Card).toBeInTheDocument();
  });

  test("renders player selection dropdowns", () => {
    render(<App />);
    const dropdowns = screen.getAllByRole("combobox");
    expect(dropdowns).toHaveLength(2);
    
    // Check if dropdowns contain all players
    const firstDropdown = dropdowns[0];
    players.forEach(player => {
      expect(firstDropdown).toHaveTextContent(player.name);
    });
  });

  test("renders ChatPanel component with initial state", () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByRole("button", { name: /Send/i });
    const welcomeMessage = screen.getByText(/Ask a question about the match!/i);
    
    expect(input).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
    expect(welcomeMessage).toBeInTheDocument();
  });

  test("displays player details correctly", () => {
    render(<App />);
    // Check specific details using more precise text matching
    expect(screen.getByText(`Age: ${players[0].age}`)).toBeInTheDocument();
    expect(screen.getByText(`Country: ${players[0].country}`)).toBeInTheDocument();
    expect(screen.getByText(`Height: ${players[0].height}`)).toBeInTheDocument();
    expect(screen.getByText(`Weight: ${players[0].weight}`)).toBeInTheDocument();
  });

  test("renders VS text between players", () => {
    render(<App />);
    const vsText = screen.getByText("VS");
    expect(vsText).toBeInTheDocument();
    expect(vsText).toHaveClass("text-4xl", "font-bold");
  });
});
