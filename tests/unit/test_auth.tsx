import { render, screen, fireEvent } from '@testing-library/react';
import Auth from '../src/components/Auth';

describe('Auth Component', () => {
  it('renders login form', () => {
    render(<Auth />);
    expect(screen.getByText('Entrar')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Senha')).toBeInTheDocument();
  });

  it('renders sign up button', () => {
    render(<Auth />);
    expect(screen.getByText('Criar Conta')).toBeInTheDocument();
  });

  it('shows logged in state when user exists', () => {
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => '{"email":"test@example.com"}'),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });

    render(<Auth />);
    expect(screen.getByText('Olá, test@example.com!')).toBeInTheDocument();
  });
});
