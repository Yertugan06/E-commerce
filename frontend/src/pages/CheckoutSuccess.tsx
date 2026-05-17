import { useParams, Link } from 'react-router-dom';

export function CheckoutSuccess() {
  const { orderId } = useParams();
  return (
    <div className="empty-state">
      <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <h2>Order Placed Successfully!</h2>
      <p>Your order #{orderId} has been placed. You'll receive a confirmation shortly.</p>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
        <Link to={`/orders/${orderId}`} className="btn-primary">
          View Order
        </Link>
        <Link to="/orders" className="btn-secondary">
          View All Orders
        </Link>
      </div>
    </div>
  );
}
