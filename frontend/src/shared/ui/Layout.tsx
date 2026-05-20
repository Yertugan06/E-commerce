import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../entities/auth/store';

export function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div>
      <header
        style={{
          background: '#1E293B',
          borderBottom: '1px solid #334155',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }}
      >
        <nav
          style={{
            maxWidth: 1200,
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0 24px',
            height: 64,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Link
              to="/"
              style={{
                padding: '8px 16px',
                fontWeight: 600,
                fontSize: 15,
                color: '#FFFFFF',
                borderRadius: 6,
              }}
            >
              Storefront
            </Link>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {user && (
              <>
                <Link
                  to="/products"
                  style={{
                    padding: '8px 16px',
                    fontWeight: 500,
                    fontSize: 15,
                    color: '#94A3B8',
                    borderRadius: 6,
                  }}
                >
                  Products
                </Link>
                <Link
                  to="/cart"
                  style={{
                    padding: '8px 16px',
                    fontWeight: 500,
                    fontSize: 15,
                    color: '#94A3B8',
                    borderRadius: 6,
                  }}
                >
                  Cart
                </Link>
                <Link
                  to="/orders"
                  style={{
                    padding: '8px 16px',
                    fontWeight: 500,
                    fontSize: 15,
                    color: '#94A3B8',
                    borderRadius: 6,
                  }}
                >
                  Orders
                </Link>
                <button
                  onClick={handleLogout}
                  className="btn-ghost"
                  style={{ marginLeft: 8 }}
                >
                  Logout
                </button>
              </>
            )}
            {!user && (
              <>
                <Link
                  to="/products"
                  style={{
                    padding: '8px 16px',
                    fontWeight: 500,
                    fontSize: 15,
                    color: '#94A3B8',
                    borderRadius: 6,
                  }}
                >
                  Products
                </Link>
                <Link
                  to="/login"
                  style={{
                    padding: '8px 16px',
                    fontWeight: 500,
                    fontSize: 15,
                    color: '#94A3B8',
                    borderRadius: 6,
                  }}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '8px 20px',
                    fontWeight: 600,
                    fontSize: 14,
                    color: '#FFFFFF',
                    background: '#10B981',
                    borderRadius: 8,
                    marginLeft: 8,
                  }}
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
