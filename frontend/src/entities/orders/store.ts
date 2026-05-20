import { create } from 'zustand';
import client from '../../shared/api/client';

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_amount: number;
  created_at: string;
  items?: OrderItem[];
}

interface OrdersState {
  orders: Order[];
  loading: boolean;
  checkout: () => Promise<Order>;
  fetchOrders: () => Promise<void>;
  fetchOrder: (id: number) => Promise<Order>;
}

export const useOrdersStore = create<OrdersState>((set) => ({
  orders: [],
  loading: false,

  checkout: async () => {
    set({ loading: true });
    try {
      const res = await client.post<Order>('/checkout');
      return res.data;
    } finally {
      set({ loading: false });
    }
  },

  fetchOrders: async () => {
    set({ loading: true });
    try {
      const res = await client.get<Order[]>('/orders');
      set({ orders: res.data });
    } catch {
      set({ orders: [] });
    } finally {
      set({ loading: false });
    }
  },

  fetchOrder: async (id) => {
    const res = await client.get<Order>(`/orders/${id}`);
    return res.data;
  },
}));
