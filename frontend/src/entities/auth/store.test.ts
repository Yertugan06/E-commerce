import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './store';

describe('useAuthStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ token: null, user: null });
  });

  it('login stores token and user in state and localStorage', () => {
    const { login } = useAuthStore.getState();
    login('test-token', { id: 1, email: 'test@test.com' });

    const state = useAuthStore.getState();
    expect(state.token).toBe('test-token');
    expect(state.user).toEqual({ id: 1, email: 'test@test.com' });
    expect(localStorage.getItem('token')).toBe('test-token');
    expect(localStorage.getItem('user')).toBe(JSON.stringify({ id: 1, email: 'test@test.com' }));
  });

  it('logout clears token and user', () => {
    const { login, logout } = useAuthStore.getState();
    login('test-token', { id: 1, email: 'test@test.com' });
    logout();

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });
});
