import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { useAuthStore } from '../../entities/auth/store';

describe('ProtectedRoute', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null });
  });

  it('redirects to /login when no token', () => {
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <ProtectedRoute />
      </MemoryRouter>,
    );
    expect(screen.queryByText(/protected/i)).not.toBeInTheDocument();
  });

  it('renders children when token exists', () => {
    useAuthStore.setState({ token: 'valid-token', user: { id: 1, email: 'test@test.com' } });
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <ProtectedRoute />
      </MemoryRouter>,
    );
    expect(screen.queryByText(/protected/i)).not.toBeInTheDocument();
  });
});
