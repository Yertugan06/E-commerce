import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useOrdersStore } from '../entities/orders/store';
import type { Order } from '../entities/orders/store';

export function OrderDetail() {
  const { orderId } = useParams();
  const { fetchOrder } = useOrdersStore();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderId) return;
    fetchOrder(Number(orderId)).then((data) => {
      setOrder(data);
    }).catch((err: unknown) => {
      const data = (err as { response?: { data?: { message?: string; detail?: string } } })?.response?.data;
      setError(data?.message || data?.detail || 'Failed to load order');
    }).finally(() => setLoading(false));
  }, [orderId, fetchOrder]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!order) return <div>Order not found</div>;

  return (
    <div>
      <Link to="/orders">&larr; Back to Orders</Link>
      <h2>Order #{order.id}</h2>
      <p>Status: {order.status}</p>
      <p>Date: {new Date(order.created_at).toLocaleString()}</p>
      <p>Total: ${order.total_amount.toFixed(2)}</p>
      <h3>Items</h3>
      <ul>
        {(order.items ?? []).map((item) => (
          <li key={item.id}>
            {item.product_name || `Product #${item.product_id}`} &times; {item.quantity} @ ${item.unit_price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
