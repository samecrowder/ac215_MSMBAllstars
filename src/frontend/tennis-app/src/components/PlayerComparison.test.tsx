import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlayerComparison } from "./PlayerComparison";

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

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("renders title and VS text", () => {
    render(<PlayerComparison players={mockPlayers} />);
    expect(screen.getByText("Game-Set-Match")).toBeInTheDocument();
    expect(screen.getByText("VS")).toBeInTheDocument();
  });

  test("renders player selection dropdowns", () => {
    render(<PlayerComparison players={mockPlayers} />);
    const dropdowns = screen.getAllByRole("combobox");
    expect(dropdowns).toHaveLength(2);
    expect(dropdowns[0]).toHaveValue("Roger Federer");
    expect(dropdowns[1]).toHaveValue("Carlos Alcaraz");
  });

  test("renders player cards", () => {
    render(<PlayerComparison players={mockPlayers} />);
    expect(screen.getAllByText("Roger Federer").length).toBeGreaterThanOrEqual(
      1,
    );
    expect(screen.getAllByText("Carlos Alcaraz").length).toBeGreaterThanOrEqual(
      1,
    );
  });

  test("allows for player selection change", async () => {
    render(<PlayerComparison players={mockPlayers} />);
    const [player1Dropdown, player2Dropdown] = screen.getAllByRole("combobox");

    await userEvent.selectOptions(player1Dropdown, "Carlos Alcaraz");
    await userEvent.selectOptions(player2Dropdown, "Roger Federer");

    expect(player1Dropdown).toHaveValue("Carlos Alcaraz");
    expect(player2Dropdown).toHaveValue("Roger Federer");
  });

  describe("API interaction tests", () => {
    beforeEach(() => {
      global.fetch = jest.fn() as jest.Mock;
    });

    test("handles predict button click", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ player_a_win_probability: 0.75 }),
      });

      render(<PlayerComparison players={mockPlayers} />);
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
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ player_a_win_probability: 0.75 }),
      });

      render(<PlayerComparison players={mockPlayers} />);
      const predictButton = screen.getByText("Predict Winner");

      fireEvent.click(predictButton);

      await waitFor(() => {
        const probabilityElements = screen.getAllByText(/%$/);
        expect(probabilityElements).toHaveLength(2);
      });
    });

    test("handles API error gracefully", async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("API Error"));

      const consoleSpy = jest.spyOn(console, "error").mockImplementation();

      render(<PlayerComparison players={mockPlayers} />);
      const predictButton = screen.getByText("Predict Winner");

      fireEvent.click(predictButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          "Error fetching prediction:",
          expect.any(Error),
        );
      });
      expect(predictButton).not.toBeDisabled();

      consoleSpy.mockRestore();
    });
  });
});
