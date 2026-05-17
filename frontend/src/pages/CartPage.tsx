import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartStore } from '../entities/cart/store';

export function CartSummary() {
  const { items, loading, updateQuantity, removeItem } = useCartStore();

  if (loading && items.length === 0) {
    return <div style={{ color: '#94A3B8', padding: '24px 0' }}>Loading cart...</div>;
  }

  if (items.length === 0) {
    return null;
  }

  return (
    <div>
      <h3 style={{ marginBottom: 16 }}>
        Cart Items ({items.length})
      </h3>
      <div className="card" style={{ padding: 0 }}>
        {items.map((item) => {
          const subtotal = item.quantity * (item.unit_price || 19.99);
          return (
            <div key={item.id} className="cart-item" style={{ padding: '16px 20px' }}>
              <div className="cart-item-image">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>
              <div className="cart-item-info">
                <h4>Product #{item.product_id}</h4>
                <p>${(item.unit_price || 19.99).toFixed(2)} each</p>
              </div>
              <div className="cart-item-quantity">
                <button
                  type="button"
                  onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                  disabled={item.quantity <= 1}
                >
                  &minus;
                </button>
                <span>{item.quantity}</span>
                <button
                  type="button"
                  onClick={() => updateQuantity(item.id, item.quantity + 1)}
                >
                  +
                </button>
              </div>
              <div className="cart-item-subtotal">${subtotal.toFixed(2)}</div>
              <button
                className="cart-item-remove"
                onClick={() => removeItem(item.id)}
                title="Remove item"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6" />
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                </svg>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function CartPage() {
  const { items, loading, fetchCart } = useCartStore();
  const navigate = useNavigate();
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (!loading && items.length === 0) {
    return (
      <div className="empty-state">
        <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="9" cy="21" r="1" />
          <circle cx="20" cy="21" r="1" />
          <path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6" />
        </svg>
        <h2>Your cart is empty</h2>
        <p>Looks like you haven't added anything yet!</p>
        <Link to="/products" className="btn-primary">
          Start Shopping
        </Link>
      </div>
    );
  }

  const subtotal = items.reduce((sum, item) => sum + item.quantity * (item.unit_price || 19.99), 0);
  const shipping = subtotal > 0 ? 0 : 0;
  const total = subtotal + shipping;

  const handleCheckout = async () => {
    setCheckoutLoading(true);
    try {
      navigate('/checkout');
    } finally {
      setCheckoutLoading(false);
    }
  };

  return (
    <div className="page">
      <h2 style={{ marginBottom: 24 }}>Shopping Cart</h2>
      <div className="cart-layout">
        <div className="cart-layout-main">
          <CartSummary />
        </div>
        <div className="cart-layout-sidebar">
          <div className="order-summary">
            <h3>Order Summary</h3>
            <div className="order-summary-row">
              <span>Subtotal</span>
              <span>${subtotal.toFixed(2)}</span>
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
            <button
              className="btn-primary"
              onClick={handleCheckout}
              disabled={checkoutLoading}
            >
              {checkoutLoading ? 'Redirecting...' : 'Proceed to Checkout'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
