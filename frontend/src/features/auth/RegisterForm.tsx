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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    try {
      const res = await client.post('/auth/register', { email, password });
      login(res.data.access_token, res.data.user);
      navigate('/');
    } catch (err: unknown) {
      const data = (err as { response?: { data?: { message?: string; detail?: string } } })?.response?.data;
      setError(data?.message || data?.detail || 'Registration failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Register</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <div>
        <label>Confirm Password</label>
        <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
      </div>
      <button type="submit" className="btn-primary">Register</button>
    </form>
  );
}
