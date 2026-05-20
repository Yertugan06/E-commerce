import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../shared/api/client';
import { useAuthStore } from '../entities/auth/store';
import { useCartStore } from '../entities/cart/store';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
}

export function Products() {
  const { user } = useAuthStore();
  const { addItem } = useCartStore();
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [addingId, setAddingId] = useState<number | null>(null);

  useEffect(() => {
    client.get<Product[]>('/products')
      .then((res) => setProducts(res.data))
      .catch(() => {
        setProducts([]);
        setFetchError('Failed to load products. Please try again.');
      })
      .finally(() => setLoading(false));
  }, []);

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

  if (loading) {
    return (
      <div className="page" style={{ textAlign: 'center', paddingTop: 48, color: '#94A3B8' }}>
        Loading products...
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="page">
        <div className="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h2>Something went wrong</h2>
          <p>{fetchError}</p>
          <button className="btn-primary" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (products.length === 0) {
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
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <div className="product-card-image">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <div className="product-card-body">
              <h3>{product.name}</h3>
              <span className="product-card-price">${product.price.toFixed(2)}</span>
              <span style={{ fontSize: 13, color: '#64748B' }}>
                {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
              </span>
              <button
                className="btn-primary"
                onClick={() => handleAddToCart(product.id)}
                disabled={addingId === product.id || product.stock < 1 || !user}
                style={{ width: '100%' }}
              >
                {addingId === product.id ? 'Adding...' : product.stock < 1 ? 'Out of Stock' : !user ? 'Login to buy' : 'Add to Cart'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
