import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Products } from './pages/Products';
import { CartPage } from './pages/CartPage';
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
          <Route element={<ProtectedRoute />}>
            <Route path="products" element={<Products />} />
            <Route path="cart" element={<CartPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
