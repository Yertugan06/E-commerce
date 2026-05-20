import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Products } from './pages/Products';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { CheckoutSuccess } from './pages/CheckoutSuccess';
import { OrderHistory } from './pages/OrderHistory';
import { OrderDetail } from './pages/OrderDetail';
import { Layout } from './shared/ui/Layout';
import { ProtectedRoute } from './features/auth/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="products" element={<Products />} />
          <Route element={<ProtectedRoute />}>
            <Route path="cart" element={<CartPage />} />
            <Route path="checkout" element={<CheckoutPage />} />
            <Route path="checkout/success/:orderId" element={<CheckoutSuccess />} />
            <Route path="orders" element={<OrderHistory />} />
            <Route path="orders/:orderId" element={<OrderDetail />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
