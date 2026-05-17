import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useOrdersStore } from '../entities/orders/store';

export function OrderHistory() {
  const { orders, loading, fetchOrders } = useOrdersStore();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  if (loading) {
    return <div>Loading orders...</div>;
  }

  if (orders.length === 0) {
    return (
      <div>
        <h2>Order History</h2>
        <p>No orders yet.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Order History</h2>
      <ul>
        {orders.map((order) => (
          <li key={order.id}>
            <Link to={`/orders/${order.id}`}>
              Order #{order.id} — {order.status} — {new Date(order.created_at).toLocaleDateString()}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
