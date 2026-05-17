# Frontend State Management

## Overview

The frontend uses **Zustand** for state management with 3 stores: auth, cart, and orders. HTTP communication is handled by a centralized **Axios client** with auth interceptors. No persistence/middleware (e.g., `zustand/middleware`) is used beyond manual `localStorage` reads in the auth store.

---

## Zustand Stores

### `useAuthStore`

**File:** `src/entities/auth/store.ts`

**State:**

| Field   | Type          | Source       |
|---------|---------------|--------------|
| `token` | `string \| null` | `localStorage.getItem('token')` read at module init |
| `user`  | `User \| null`   | `localStorage.getItem('user')` parsed at module init |

**Actions:**

| Action | Signature | Behavior |
|--------|-----------|----------|
| `login` | `(token: string, user: User) => void` | Writes `token` and serialized `user` to `localStorage`, updates state |
| `logout` | `() => void` | Removes `token` and `user` from `localStorage`, nullifies state |

**Usage:** Components call `useAuthStore(state => state.token)` to check auth status. The `login` action is called after successful `POST /auth/register` or `POST /auth/login`.

### `useCartStore`

**File:** `src/entities/cart/store.ts`

**State:**

| Field     | Type            | Default |
|-----------|-----------------|---------|
| `items`   | `CartItem[]`    | `[]`    |
| `loading` | `boolean`       | `false` |

**Actions:**

| Action | Signature | Behavior |
|--------|-----------|----------|
| `fetchCart` | `() => Promise<void>` | `GET /cart` → sets `items` |
| `addItem` | `(product_id: number, quantity: number) => Promise<void>` | `POST /cart/items` → re-fetches cart |
| `updateQuantity` | `(item_id: number, quantity: number) => Promise<void>` | `PUT /cart/items/{item_id}` → re-fetches cart |
| `removeItem` | `(item_id: number) => Promise<void>` | `DELETE /cart/items/{item_id}` → re-fetches cart |

**Pattern:** Every mutating action (add/update/delete) calls `fetchCart()` afterward to keep local state in sync. This is simple but generates extra requests — an optimization target for later.

### `useOrdersStore`

**File:** `src/entities/orders/store.ts`

**State:**

| Field     | Type      | Default |
|-----------|-----------|---------|
| `orders`  | `Order[]` | `[]`    |
| `loading` | `boolean` | `false` |

**Actions:**

| Action | Signature | Behavior |
|--------|-----------|----------|
| `checkout` | `() => Promise<Order>` | `POST /checkout` → returns the created order (caller navigates to success page) |
| `fetchOrders` | `() => Promise<void>` | `GET /orders` → sets `orders` |
| `fetchOrder` | `(id: number) => Promise<Order>` | `GET /orders/{id}` → returns order (caller manages state) |

**Note:** `checkout()` returns the order directly rather than storing it in state, since the caller immediately navigates to the success page. `fetchOrder()` also returns the order without storing — used for the order detail page.

---

## API Client

**File:** `src/shared/api/client.ts`

```typescript
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});
```

### Request Interceptor

Attaches JWT from `localStorage`:
```
Authorization: Bearer <token>
```

### Response Interceptor

On **401** responses:
1. Clears `token` and `user` from `localStorage`
2. Redirects to `/login` via `window.location.href`

This handles token expiry and invalid credentials transparently across all API calls.

---

## Data Flow Pattern

```
User Action (click, submit)
  │
  ▼
React Component
  │
  ├─ calls store action (e.g. useCartStore.addItem)
  │
  ▼
Zustand Store Action
  │
  ├─ calls client.<method>() (e.g. client.post('/cart/items', body))
  │
  ▼
Axios Client
  │
  ├─ Request interceptor attaches Bearer token
  │
  ▼
Backend API
  │
  ├─ Response interceptor catches 401 → redirect
  │
  ▼
Zustand Store Action (continued)
  │
  ├─ updates local state via set()
  │
  ▼
React Component re-renders with new state
```

---

## Store Interaction Matrix

| Event | Auth Store | Cart Store | Orders Store |
|-------|-----------|------------|--------------|
| User logs in | stores token + user | — | — |
| User logs out | clears token + user | — | — |
| Product added to cart | — | re-fetches | — |
| Cart page visited | — | `fetchCart()` | — |
| Checkout submitted | — | — | `checkout()` → clears cart on backend |
| Orders page visited | — | — | `fetchOrders()` |
| Order detail visited | — | — | `fetchOrder(id)` |

Stores operate independently — there is no cross-store communication. When checkout succeeds, the cart store is not automatically cleared; the backend deletes cart items, so the next `fetchCart()` call reflects the empty state.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

Set via `frontend/.env` file or docker-compose environment. In Docker, this is `http://backend:8000`.

---

## Key Files

| File | Purpose |
|------|---------|
| `src/entities/auth/store.ts` | Auth state (token, user, login, logout) |
| `src/entities/cart/store.ts` | Cart state (items, CRUD actions) |
| `src/entities/orders/store.ts` | Orders state (checkout, fetch) |
| `src/shared/api/client.ts` | Axios instance with auth interceptors |
| `src/features/auth/ProtectedRoute.tsx` | Route guard using `useAuthStore.token` |
| `src/features/auth/LoginForm.tsx` | Login form, calls `store.login()` on success |
| `src/features/auth/RegisterForm.tsx` | Register form, calls `store.login()` on success |
