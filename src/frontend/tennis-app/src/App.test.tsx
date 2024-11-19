import { render, screen } from '@testing-library/react';
import React from 'react';
import App from './App';

test('renders Game-Set-Match', () => {
  render(<App />);
  const linkElement = screen.getByText(/Game-Set-Match/i);
  expect(linkElement).toBeInTheDocument();
});
