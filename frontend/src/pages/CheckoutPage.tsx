import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '../entities/cart/store';
import { useOrdersStore } from '../entities/orders/store';

export function CheckoutPage() {
  const navigate = useNavigate();
  const { items, fetchCart } = useCartStore();
  const { checkout } = useOrdersStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleCheckout = async () => {
    setLoading(true);
    setError('');
    try {
      const order = await checkout();
      navigate(`/checkout/success/${order.id}`);
    } catch (err: unknown) {
      const data = (err as { response?: { data?: { message?: string; detail?: string } } })?.response?.data;
      setError(data?.message || data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="page">
        <div className="empty-state" style={{ minHeight: 'auto' }}>
          <h2>Checkout</h2>
          <p>Your cart is empty. Add some products first.</p>
          <button className="btn-primary" onClick={() => navigate('/products')}>
            Browse Products
          </button>
        </div>
      </div>
    );
  }

  const total = items.reduce((sum, item) => sum + item.quantity * (item.unit_price || 19.99), 0);

  return (
    <div className="page">
      <h2 style={{ marginBottom: 24 }}>Checkout</h2>
      {error && (
        <div style={{ color: '#EF4444', marginBottom: 16, fontSize: 14 }}>{error}</div>
      )}
      <div className="cart-layout">
        <div className="cart-layout-main">
          <div className="card">
            <h3 style={{ marginBottom: 16 }}>Cart Summary</h3>
            {items.map((item) => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-image">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
                <div className="cart-item-info">
                  <h4>Product #{item.product_id}</h4>
                  <p>${(item.unit_price || 19.99).toFixed(2)} &times; {item.quantity}</p>
                </div>
                <div className="cart-item-subtotal">
                  ${(item.quantity * (item.unit_price || 19.99)).toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="cart-layout-sidebar">
          <div className="order-summary">
            <h3>Order Summary</h3>
            <div className="order-summary-row">
              <span>Subtotal</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <div className="order-summary-row">
              <span>Shipping</span>
              <span style={{ color: '#10B981' }}>Free</span>
            </div>
            <div className="order-summary-divider" />
            <div className="order-summary-total">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <button className="btn-primary" onClick={handleCheckout} disabled={loading}>
              {loading ? 'Processing...' : 'Place Order'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
