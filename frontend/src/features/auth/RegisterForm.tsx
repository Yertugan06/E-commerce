import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../shared/api/client';
import { useAuthStore } from '../../entities/auth/store';

export function RegisterForm() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    setSubmitting(true);
    try {
      const res = await client.post('/auth/register', { email, password });
      login(res.data.access_token, res.data.user);
      navigate('/products');
    } catch (err: unknown) {
      const data = (err as { response?: { data?: { message?: string; detail?: string } } })?.response?.data;
      setError(data?.message || data?.detail || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Register</h2>
      {error && <p style={{ color: '#F87171', background: '#1E1E1E', padding: '8px 12px', borderRadius: 4 }}>{error}</p>}
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <div>
        <label htmlFor="confirm">Confirm Password</label>
        <input id="confirm" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
      </div>
      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}
