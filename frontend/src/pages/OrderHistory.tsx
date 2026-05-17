import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useOrdersStore } from '../entities/orders/store';

function statusBadgeClass(status: string): string {
  switch (status) {
    case 'delivered':
    case 'shipped':
      return 'badge badge-success';
    case 'pending':
    case 'confirmed':
      return 'badge badge-warning';
    case 'cancelled':
      return 'badge badge-error';
    default:
      return 'badge badge-info';
  }
}

function statusLabel(status: string): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function OrderHistory() {
  const { orders, loading, fetchOrders } = useOrdersStore();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  if (loading) {
    return (
      <div className="page">
        <div style={{ textAlign: 'center', padding: '48px 0', color: '#94A3B8' }}>
          Loading orders...
        </div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="empty-state">
        <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
          <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
          <line x1="12" y1="22.08" x2="12" y2="12" />
        </svg>
        <h2>No orders placed yet</h2>
        <p>Your order history will appear here once you make your first purchase.</p>
        <Link to="/products" className="btn-primary">
          Explore Products
        </Link>
      </div>
    );
  }

  return (
    <div className="page">
      <h2 style={{ marginBottom: 24 }}>Order History</h2>
      {orders.map((order) => (
        <Link to={`/orders/${order.id}`} key={order.id} className="order-row" style={{ display: 'flex', textDecoration: 'none' }}>
          <div className="order-row-info">
            <h4>Order #{order.id}</h4>
            <p>{new Date(order.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
          </div>
          <div className="order-row-right">
            <div>
              <div className="order-row-total">${order.total_amount.toFixed(2)}</div>
              <span className={statusBadgeClass(order.status)} style={{ marginTop: 4 }}>
                {statusLabel(order.status)}
              </span>
            </div>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </Link>
      ))}
    </div>
  );
}
