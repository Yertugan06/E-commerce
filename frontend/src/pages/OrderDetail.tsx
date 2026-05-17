import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useOrdersStore } from '../entities/orders/store';

interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
}

interface Order {
  id: number;
  status: string;
  total_amount: number;
  created_at: string;
  items: OrderItem[];
}

export function OrderDetail() {
  const { orderId } = useParams();
  const { fetchOrder } = useOrdersStore();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderId) return;
    setLoading(true);
    fetchOrder(Number(orderId)).then((data: any) => {
      setOrder(data as Order);
    }).catch((err) => setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to load order'))
      .finally(() => setLoading(false));
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
        {order.items.map((item) => (
          <li key={item.id}>
            Product #{item.product_id} &times; {item.quantity} @ ${item.unit_price.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
