import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../entities/auth/store';

export function Home() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '120px 24px 80px',
        textAlign: 'center',
      }}
    >
      {user && (
        <p
          style={{
            fontSize: 14,
            color: '#64748B',
            marginBottom: 16,
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
          }}
        >
          Welcome back, {user.email}
        </p>
      )}

      <h1
        style={{
          fontSize: 56,
          fontWeight: 700,
          color: '#FFFFFF',
          letterSpacing: '-1.5px',
          lineHeight: 1.1,
          marginBottom: 16,
          maxWidth: 600,
        }}
      >
        Discover Great Products
      </h1>

      <p
        style={{
          fontSize: 18,
          color: '#94A3B8',
          lineHeight: 1.6,
          maxWidth: 480,
          marginBottom: 40,
        }}
      >
        Browse our curated collection of premium products. Fast checkout, order tracking, and more.
      </p>

      <button
        onClick={() => navigate('/products')}
        className="btn-primary"
        style={{ fontSize: 16, padding: '14px 32px' }}
      >
        Browse Products
      </button>
    </div>
  );
}
