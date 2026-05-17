import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../entities/auth/store';
import { useCartStore } from '../entities/cart/store';

const MOCK_PRODUCTS = [
  { id: 101, title: 'Wireless Headphones', price: 79.99 },
  { id: 102, title: 'Smart Watch', price: 199.99 },
  { id: 103, title: 'Bluetooth Speaker', price: 49.99 },
  { id: 104, title: 'Laptop Stand', price: 34.99 },
];

export function Products() {
  const { user } = useAuthStore();
  const { addItem } = useCartStore();
  const navigate = useNavigate();
  const [addingId, setAddingId] = useState<number | null>(null);

  const handleAddToCart = async (productId: number) => {
    if (!user) {
      navigate('/login');
      return;
    }
    setAddingId(productId);
    try {
      await addItem(productId, 1);
    } finally {
      setAddingId(null);
    }
  };

  if (MOCK_PRODUCTS.length === 0) {
    return (
      <div className="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
          <line x1="8" y1="21" x2="16" y2="21" />
          <line x1="12" y1="17" x2="12" y2="21" />
        </svg>
        <h2>No products found</h2>
        <p>Check back later for new arrivals.</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>Products</h2>
      </div>
      <div className="product-grid">
        {MOCK_PRODUCTS.map((product) => (
          <div key={product.id} className="product-card">
            <div className="product-card-image">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <div className="product-card-body">
              <h3>{product.title}</h3>
              <span className="product-card-price">${product.price.toFixed(2)}</span>
              <button
                className="btn-primary"
                onClick={() => handleAddToCart(product.id)}
                disabled={addingId === product.id}
                style={{ width: '100%' }}
              >
                {addingId === product.id ? 'Adding...' : 'Add to Cart'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
