import {
  fireEvent,
  render,
  screen,
  waitFor,
  act,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlayerComparison } from "./PlayerComparison";
import { useState } from "react";

describe("PlayerComparison", () => {
  const mockPlayers = [
    {
      id: "roger-federer",
      name: "Roger Federer",
      age: "42",
      country: "Switzerland",
      height: "6'1\"",
      weight: "187 lbs",
      imageUrl: "https://example.com/federer.jpg",
      gradientFrom: "#ff0000",
      gradientTo: "#ff9999",
    },
    {
      id: "carlos-alcaraz",
      name: "Carlos Alcaraz",
      age: "21 (2003/05/05)",
      country: "Spain",
      height: "6'0\" (183cm)",
      weight: "163 lbs (74kg)",
      imageUrl: "/images/carlos_alcaraz.png",
    },
  ];

  // Wrapper component to manage state during tests
  const TestWrapper = () => {
    const [matchup, setMatchup] = useState({
      player1: mockPlayers[0], // Roger Federer
      player2: mockPlayers[1], // Carlos Alcaraz
    });

    return (
      <PlayerComparison
        allowInitialFetch={false}
        players={mockPlayers}
        matchup={matchup}
        setMatchup={setMatchup}
      />
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ player_a_win_probability: 0.75 }),
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("renders title and VS text", () => {
    render(<TestWrapper />);
    expect(screen.getByText("Game-Set-Match")).toBeInTheDocument();
    expect(screen.getByText("VS")).toBeInTheDocument();
  });

  test("renders player selection dropdowns", () => {
    render(<TestWrapper />);
    const dropdowns = screen.getAllByRole("combobox");
    expect(dropdowns).toHaveLength(2);
    expect(dropdowns[0]).toHaveValue("Roger Federer");
    expect(dropdowns[1]).toHaveValue("Carlos Alcaraz");
  });

  test("renders player cards", () => {
    render(<TestWrapper />);
    expect(screen.getAllByText("Roger Federer").length).toBeGreaterThanOrEqual(
      1,
    );
    expect(screen.getAllByText("Carlos Alcaraz").length).toBeGreaterThanOrEqual(
      1,
    );
  });

  test("allows for player selection change", async () => {
    render(<TestWrapper />);
    const [player1Dropdown, player2Dropdown] = screen.getAllByRole("combobox");

    await userEvent.selectOptions(player1Dropdown, "Carlos Alcaraz");
    expect(player1Dropdown).toHaveValue("Carlos Alcaraz");

    await userEvent.selectOptions(player2Dropdown, "Roger Federer");
    expect(player2Dropdown).toHaveValue("Roger Federer");
  });

  describe("API interaction tests", () => {
    test("handles predict button click", async () => {
      render(<TestWrapper />);

      const predictButton = screen.getByText("Predict Winner");

      fireEvent.click(predictButton);
      expect(predictButton).toBeDisabled();
      expect(screen.getByText("Loading...")).toBeInTheDocument();

      await waitFor(() => {
        expect(predictButton).not.toBeDisabled();
      });
      expect(screen.getByText("Predict Winner")).toBeInTheDocument();
    });

    test("displays win probability after predict button click", async () => {
      render(<TestWrapper />);
      const predictButton = screen.getByText("Predict Winner");

      await act(async () => {
        fireEvent.click(predictButton);
        // Wait for state updates to complete
        await Promise.resolve();
      });

      await waitFor(() => {
        const probabilityElements = screen.getAllByText(/%$/);
        expect(probabilityElements).toHaveLength(2);
      });
    });

    test("handles API error gracefully", async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error("API Error"));
      const consoleSpy = jest.spyOn(console, "error").mockImplementation();

      render(<TestWrapper />);
      const predictButton = screen.getByText("Predict Winner");

      await act(async () => {
        fireEvent.click(predictButton);
        // Wait for state updates to complete
        await Promise.resolve();
      });

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          "Error fetching prediction:",
          expect.any(Error),
        );
      });

      expect(screen.getByText("Predict Winner")).toBeInTheDocument();
      consoleSpy.mockRestore();
    });
  });
});
