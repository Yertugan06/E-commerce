import { useParams, Link } from 'react-router-dom';

export function CheckoutSuccess() {
  const { orderId } = useParams();
  return (
    <div>
      <h2>Order Placed Successfully!</h2>
      <p>Your order #{orderId} has been placed.</p>
      <Link to={`/orders/${orderId}`}>View Order</Link>
      <br />
      <Link to="/orders">View All Orders</Link>
    </div>
  );
}
