import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '../entities/cart/store';
import { useOrdersStore } from '../entities/orders/store';

export function CheckoutPage() {
  const navigate = useNavigate();
  const { items } = useCartStore();
  const { checkout } = useOrdersStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCheckout = async () => {
    setLoading(true);
    setError('');
    try {
      const order = await checkout();
      navigate(`/checkout/success/${order.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div>
        <h2>Checkout</h2>
        <p>Your cart is empty. Add some products first.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Checkout</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <h3>Cart Summary</h3>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            Product #{item.product_id} &times; {item.quantity}
          </li>
        ))}
      </ul>
      <button onClick={handleCheckout} disabled={loading}>
        {loading ? 'Processing...' : 'Place Order'}
      </button>
    </div>
  );
}
