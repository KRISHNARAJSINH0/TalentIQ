import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

// Mock both useAuth and NotificationBell
vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../components/NotificationBell', () => ({
  default: () => <div data-testid="mock-bell">Bell</div>,
}));

describe('Navbar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const setupMockAuth = (isAuthenticated, user) => {
    useAuth.mockReturnValue({
      isAuthenticated,
      user,
      logout: vi.fn(),
    });
  };

  it('renders landing page links when unauthenticated', () => {
    setupMockAuth(false, null);

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    // Desktop features and mobile features may both be present
    expect(screen.getAllByText('Features')[0]).toBeInTheDocument();
    expect(screen.getAllByText('About')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Login')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Get Started')[0]).toBeInTheDocument();
  });

  it('renders application navigation when authenticated', () => {
    setupMockAuth(true, { first_name: 'John', role: 'candidate' });

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    expect(screen.getAllByText('Resumes')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Profile')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Portfolio')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Career AI')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Timeline')[0]).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getAllByText('Logout')[0]).toBeInTheDocument();
    expect(screen.getByTestId('mock-bell')).toBeInTheDocument();
  });

  it('renders admin links only when role is admin', () => {
    // 1. Admin case (Use different first_name to avoid clashing with 'Admin' link text)
    setupMockAuth(true, { first_name: 'SuperAdminUser', role: 'admin' });

    const { rerender } = render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    expect(screen.getAllByText('Admin')[0]).toBeInTheDocument();

    // 2. Candidate case
    setupMockAuth(true, { first_name: 'John', role: 'candidate' });

    rerender(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    expect(screen.queryByText('Admin')).not.toBeInTheDocument();
  });
});
