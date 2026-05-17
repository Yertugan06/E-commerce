import { useEffect } from 'react';
import { useCartStore } from '../../entities/cart/store';
import { QuantitySelector } from './QuantitySelector';

export function CartSummary() {
  const { items, loading, fetchCart, updateQuantity, removeItem } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (loading && items.length === 0) {
    return <div>Loading cart...</div>;
  }

  if (items.length === 0) {
    return <div>Your cart is empty.</div>;
  }

  return (
    <div>
      <h3>Cart ({items.length} items)</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {items.map((item) => (
          <li key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <span>Product #{item.product_id}</span>
            <QuantitySelector
              value={item.quantity}
              onChange={(qty) => updateQuantity(item.id, qty)}
            />
            <button onClick={() => removeItem(item.id)}>Remove</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
