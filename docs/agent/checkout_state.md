# Checkout State & Stock Locking

## Overview

The checkout flow converts a user's cart into an order. The MVP uses a simplistic transaction: fetch cart items → process payment (stub) → create order → clear cart. **No stock locking or inventory management** is implemented.

---

## Checkout Flow

```
POST /checkout (Authenticated)
  │
  ├─ 1. ensure_cart_exists(db, user_id)
  │      Creates cart row if missing
  │
  ├─ 2. fetch cart items from cart_items table
  │
  ├─ 3. if cart is empty → raise CART_EMPTY (400)
  │
  ├─ 4. process_payment(total) → stub, always returns True
  │
  ├─ 5. create_order_from_cart(db, user_id, items)
  │      Creates Order row + OrderItem rows (unit_price = 0.0)
  │
  ├─ 6. delete all CartItem rows for this cart
  │
  ├─ 7. commit transaction
  │
  └─ 8. return OrderRead with items
```

### Endpoints

| Method | Path | Auth | Returns |
|--------|------|------|---------|
| `POST` | `/checkout` | Required | `OrderRead` |
| `GET` | `/orders` | Required | `list[OrderListRead]` |
| `GET` | `/orders/{order_id}` | Required | `OrderRead` |

---

## Order Status Lifecycle

```
                    ┌──────────┐
                    │ PENDING  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ CONFIRMED│
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ SHIPPED  │
                    └────┬─────┘
                         │
                    ┌────▼──────┐
                    │ DELIVERED │
                    └───────────┘

                    ┌───────────┐
         CANCELLED ◄─── (any state)
                    └───────────┘
```

- **PENDING** — Initial state after checkout
- **CONFIRMED** — Payment confirmed (no separate step in MVP)
- **SHIPPED** — Order shipped
- **DELIVERED** — Order delivered
- **CANCELLED** — Can be cancelled from any state (admin action, not yet exposed via API)

All orders start at `PENDING`. The MVP creates no endpoint to transition status — this is reserved for future admin functionality.

**Enum definition:** `backend/app/features/orders/domain/__init__.py`

---

## Stock Locking

**Not implemented in the MVP.**

There is no `products` table, no inventory/stock column, and no locking mechanism. The `product_id` in `cart_items` and `order_items` is a plain integer with no FK constraint. This means:

- Multiple users can "checkout" the same `product_id` concurrently without any conflict
- No `SELECT ... FOR UPDATE` or pessimistic locks are used
- No optimistic locking (version column) is implemented
- No reservation timeout or cart expiry exists

**Future considerations:**
- Add a `products` table with a `stock` column (non-negative integer)
- Use row-level locking (`SELECT ... FOR UPDATE`) inside the checkout transaction
- Decrement stock atomically: `UPDATE products SET stock = stock - :quantity WHERE id = :product_id AND stock >= :quantity`
- Roll back the entire transaction if any product has insufficient stock

---

## Payment Processing

The payment system is a **stub** in `backend/app/features/checkout/payment.py`:

```python
def process_payment(amount: float) -> bool:
    return True
```

In the MVP, all payments are accepted. A production system would integrate with a payment provider (Stripe, etc.) and handle:
- Payment intent creation
- Webhook confirmation
- Refund processing
- Payment status tracking on the order

---

## Transactional Behavior

The checkout function uses the **same database session** for all operations. Since SQLModel/SQLAlchemy wraps this in a single transaction:
1. Order + OrderItems are created
2. CartItems are deleted
3. `db.commit()` persists everything atomically
4. If any step fails, `db.rollback()` reverts all changes

There is **no distributed transaction** between payment and DB — the payment stub does not participate in the DB transaction.

---

## Concurrent Checkouts (Race Conditions)

Since no stock locking exists, concurrent checkouts by the same user are technically possible. However:
- Each user has one cart
- Cart items are deleted after checkout
- A second concurrent checkout would find an empty cart and return `CART_EMPTY (400)`

For the same user, this is safe. For different users competing for the same `product_id`, no protection exists.

---

## Key Files

| File | Purpose |
|------|---------|
| `app/features/checkout/router.py` | `POST /checkout`, `GET /orders`, `GET /orders/{id}` |
| `app/features/checkout/use_cases.py` | `checkout()`, `get_user_orders()`, `get_order_detail()` |
| `app/features/checkout/payment.py` | `process_payment()` stub |
| `app/features/orders/repositories.py` | `create_order_from_cart()`, `get_orders_by_user_id()`, `get_order_by_id()` |
| `app/features/orders/models.py` | `Order`, `OrderItem` SQLModel definitions |
| `app/features/orders/domain/__init__.py` | `OrderStatus` enum |
| `app/features/orders/schemas.py` | `OrderRead`, `OrderListRead`, `OrderItemRead` |
