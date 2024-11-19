import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PlayerComparison } from './PlayerComparison';

describe('PlayerComparison', () => {
  const mockPlayers = [
    {
      id: 'roger-federer',
      name: 'Roger Federer',
      age: 42,
      country: 'Switzerland',
      height: '6\'1"',
      weight: '187 lbs',
      imageUrl: 'https://example.com/federer.jpg',
      gradientFrom: '#ff0000',
      gradientTo: '#ff9999',
    },
    {
      id: 'rafael-nadal',
      name: 'Rafael Nadal',
      age: 37,
      country: 'Spain',
      height: '6\'1"',
      weight: '187 lbs',
      imageUrl: 'https://example.com/nadal.jpg',
      gradientFrom: '#0000ff',
      gradientTo: '#9999ff',
    },
  ];

  const mockOnPredictClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders title and VS text', () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    expect(screen.getByText('Game-Set-Match')).toBeInTheDocument();
    expect(screen.getByText('VS')).toBeInTheDocument();
  });

  test('renders player selection dropdowns', () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    const dropdowns = screen.getAllByRole('combobox');
    expect(dropdowns).toHaveLength(2);
    expect(dropdowns[0]).toHaveValue('Roger Federer');
    expect(dropdowns[1]).toHaveValue('Rafael Nadal');
  });

  test('renders player cards', () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    expect(screen.getAllByText('Roger Federer').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Rafael Nadal').length).toBeGreaterThanOrEqual(1);
  });

  test('allows for player selection change', async () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    const [player1Dropdown, player2Dropdown] = screen.getAllByRole('combobox');

    await userEvent.selectOptions(player1Dropdown, 'Rafael Nadal');
    await userEvent.selectOptions(player2Dropdown, 'Roger Federer');

    expect(player1Dropdown).toHaveValue('Rafael Nadal');
    expect(player2Dropdown).toHaveValue('Roger Federer');
  });

  test('handles predict button click', async () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    const predictButton = screen.getByText('Predict Winner');

    fireEvent.click(predictButton);
    expect(predictButton).toBeDisabled();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    await waitFor(() => {
      expect(predictButton).not.toBeDisabled();
    });
    expect(screen.getByText('Predict Winner')).toBeInTheDocument();
  });

  test('displays win probability', () => {
    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    const probabilityElements = screen.getAllByText(/%$/);
    expect(probabilityElements).toHaveLength(2);
  });

  test('handles API error gracefully', async () => {
    // Mock fetch to simulate error
    global.fetch = jest.fn(() =>
      Promise.reject(new Error('API Error'))
    ) as jest.Mock;

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    render(<PlayerComparison players={mockPlayers} onPredictClick={mockOnPredictClick} />);
    const predictButton = screen.getByText('Predict Winner');

    fireEvent.click(predictButton);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching prediction:', expect.any(Error));
    });
    expect(predictButton).not.toBeDisabled();

    consoleSpy.mockRestore();
  });
});
