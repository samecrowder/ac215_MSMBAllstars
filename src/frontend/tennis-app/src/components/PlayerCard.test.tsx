import { render, screen } from '@testing-library/react';
import { PlayerCard } from './PlayerCard';

describe('PlayerCard', () => {
  const mockPlayerData = {
    id: 'roger-federer',
    name: 'Roger Federer',
    age: 42,
    country: 'Switzerland',
    height: '6\'1"',
    weight: '187 lbs',
    imageUrl: 'https://example.com/federer.jpg',
  };

  test('renders player information correctly', () => {
    render(<PlayerCard {...mockPlayerData} />);
    
    expect(screen.getByText('Roger Federer')).toBeInTheDocument();
    expect(screen.getByText('Age: 42')).toBeInTheDocument();
    expect(screen.getByText('Country: Switzerland')).toBeInTheDocument();
    expect(screen.getByText('Height: 6\'1"')).toBeInTheDocument();
    expect(screen.getByText('Weight: 187 lbs')).toBeInTheDocument();
  });

  test('renders player image with correct alt text', () => {
    render(<PlayerCard {...mockPlayerData} />);
    
    const image = screen.getByAltText('Roger Federer') as HTMLImageElement;
    expect(image).toBeInTheDocument();
    expect(image.src).toBe('https://example.com/federer.jpg');
  });

  test('applies default gradient colors', () => {
    render(<PlayerCard {...mockPlayerData} />);
    
    const image = screen.getByAltText('Roger Federer');
    expect(image).toHaveStyle({
      background: 'linear-gradient(to bottom, #ffffff, #f3f4f6)'
    });
  });

  test('applies custom gradient colors', () => {
    render(
      <PlayerCard 
        {...mockPlayerData} 
        gradientFrom="#ff0000" 
        gradientTo="#0000ff" 
      />
    );
    
    const image = screen.getByAltText('Roger Federer');
    expect(image).toHaveStyle({
      background: 'linear-gradient(to bottom, #ff0000, #0000ff)'
    });
  });

  test('renders with correct CSS classes', () => {
    render(<PlayerCard {...mockPlayerData} />);
    
    // eslint-disable-next-line testing-library/no-node-access
    const card = screen.getByRole('img').parentElement;
    expect(card).toHaveClass('border', 'p-4', 'rounded-lg', 'w-80');
  });
});
