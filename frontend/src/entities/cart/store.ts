import { create } from 'zustand';
import client from '../../shared/api/client';

interface CartItem {
  id: number;
  cart_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface Cart {
  id: number;
  user_id: number;
  items: CartItem[];
}

interface CartState {
  items: CartItem[];
  loading: boolean;
  error: string | null;
  fetchCart: () => Promise<void>;
  addItem: (product_id: number, quantity: number) => Promise<void>;
  updateQuantity: (item_id: number, quantity: number) => Promise<void>;
  removeItem: (item_id: number) => Promise<void>;
  clearCart: () => void;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetchCart: async () => {
    set({ loading: true, error: null });
    try {
      const res = await client.get<Cart>('/cart');
      set({ items: res.data.items });
    } catch {
      set({ error: 'Failed to load cart' });
    } finally {
      set({ loading: false });
    }
  },

  addItem: async (product_id, quantity) => {
    await client.post('/cart/items', { product_id, quantity });
    await get().fetchCart();
  },

  updateQuantity: async (item_id, quantity) => {
    await client.put(`/cart/items/${item_id}`, { quantity });
    await get().fetchCart();
  },

  removeItem: async (item_id) => {
    await client.delete(`/cart/items/${item_id}`);
    await get().fetchCart();
  },

  clearCart: () => set({ items: [], error: null }),
}));
