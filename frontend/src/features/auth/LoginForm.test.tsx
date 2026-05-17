import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginForm } from './LoginForm';
import { useAuthStore } from '../../entities/auth/store';
import client from '../../shared/api/client';

vi.mock('../../shared/api/client', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../../shared/api/client')>();
  return {
    default: {
      ...mod.default,
      post: vi.fn(),
    },
  };
});

function renderLoginForm() {
  return render(
    <BrowserRouter>
      <LoginForm />
    </BrowserRouter>,
  );
}

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({ token: null, user: null });
  });

  it('renders email, password inputs and submit button', () => {
    renderLoginForm();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('shows error on API failure', async () => {
    (client.post as any).mockRejectedValue({
      response: { data: { detail: 'Invalid credentials' } },
    });

    renderLoginForm();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), 'test@test.com');
    await user.type(screen.getByLabelText(/password/i), 'wrong');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  });

  it('calls login on success', async () => {
    (client.post as any).mockResolvedValue({
      data: { access_token: 'token', user: { id: 1, email: 'test@test.com' } },
    });

    renderLoginForm();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email/i), 'test@test.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    const state = useAuthStore.getState();
    expect(state.token).toBe('token');
    expect(state.user?.email).toBe('test@test.com');
  });
});
