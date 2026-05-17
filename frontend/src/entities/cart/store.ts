import { create } from 'zustand';
import client from '../../shared/api/client';

interface CartItem {
  id: number;
  cart_id: number;
  product_id: number;
  quantity: number;
  unit_price?: number;
}

interface Cart {
  id: number;
  user_id: number;
  items: CartItem[];
}

interface CartState {
  items: CartItem[];
  loading: boolean;
  fetchCart: () => Promise<void>;
  addItem: (product_id: number, quantity: number) => Promise<void>;
  updateQuantity: (item_id: number, quantity: number) => Promise<void>;
  removeItem: (item_id: number) => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  loading: false,

  fetchCart: async () => {
    set({ loading: true });
    try {
      const res = await client.get<Cart>('/cart');
      set({ items: res.data.items });
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
}));
