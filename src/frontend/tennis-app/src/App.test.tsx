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

  test("renders ChatPanel component", () => {
    render(<App />);
    // Check if chat panel is rendered with its initial state
    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Send/i })).toBeInTheDocument();
  });

  test("initial state has correct players", () => {
    render(<App />);
    // Verify player details are displayed
    expect(screen.getByText(`Age: ${players[0].age}`)).toBeInTheDocument();
    expect(screen.getByText(`Age: ${players[1].age}`)).toBeInTheDocument();
    expect(screen.getByText(`Country: ${players[0].country}`)).toBeInTheDocument();
    expect(screen.getByText(`Country: ${players[1].country}`)).toBeInTheDocument();
  });
});
