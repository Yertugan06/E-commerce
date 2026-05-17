# Database Schema

## Overview

The MVP uses 5 SQLModel tables managed via Alembic. Tables are created automatically on startup via `SQLModel.metadata.create_all` in `app/core/database.py` (lifespan hook). No products table exists — `product_id` fields are plain integers referencing an external or future catalog.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐
│    users    │       │    carts     │
├─────────────┤       ├──────────────┤
│ id (PK)     │◄──────│ user_id (FK) │
│ email (UQ)  │       │ id (PK)      │
│ hashed_pwd  │       └──────┬───────┘
│ role        │              │ 1
│ created_at  │              │
└─────────────┘       ┌──────┴────────┐
                      │  cart_items   │
                      ├───────────────┤
                      │ id (PK)       │
                      │ cart_id (FK)  │
                      │ product_id    │
                      │ quantity      │
                      └───────────────┘

┌─────────────┐       ┌──────────────┐
│    users    │       │    orders    │
├─────────────┤       ├──────────────┤
│ id (PK)     │◄──────│ user_id (FK) │
│             │       │ id (PK)      │
│             │       │ status       │
│             │       │ total_amount │
│             │       │ created_at   │
│             │       └──────┬───────┘
│             │              │ 1
│             │       ┌──────┴────────┐
│             │       │  order_items  │
│             │       ├───────────────┤
│             │       │ id (PK)       │
│             │       │ order_id (FK) │
│             │       │ product_id    │
│             │       │ quantity      │
│             │       │ unit_price    │
│             │       └───────────────┘
```

---

## Tables

### `users`

| Column          | Type         | Constraints                |
|-----------------|--------------|----------------------------|
| `id`            | int          | PK, auto-increment         |
| `email`         | str          | NOT NULL, UNIQUE, indexed  |
| `hashed_password` | str        | NOT NULL                   |
| `role`          | UserRole     | NOT NULL, default: `customer` |
| `created_at`    | datetime     | NOT NULL, default: `utcnow()` |

- `UserRole` enum: `customer`, `admin`
- **File:** `backend/app/features/users/models.py`

### `carts`

| Column    | Type | Constraints                 |
|-----------|------|-----------------------------|
| `id`      | int  | PK, auto-increment          |
| `user_id` | int  | NOT NULL, UNIQUE, FK → users.id |

- One cart per user (enforced by unique constraint on `user_id`)
- **File:** `backend/app/features/cart/models.py`

### `cart_items`

| Column       | Type | Constraints       |
|--------------|------|-------------------|
| `id`         | int  | PK, auto-increment |
| `cart_id`    | int  | NOT NULL, FK → carts.id |
| `product_id` | int  | NOT NULL          |
| `quantity`   | int  | NOT NULL, default: 1 |

- **File:** `backend/app/features/cart/models.py`

### `orders`

| Column         | Type         | Constraints                |
|----------------|--------------|----------------------------|
| `id`           | int          | PK, auto-increment         |
| `user_id`      | int          | NOT NULL, FK → users.id    |
| `status`       | OrderStatus  | NOT NULL, default: `pending` |
| `total_amount` | float        | NOT NULL, default: 0.0     |
| `created_at`   | datetime     | NOT NULL, default: `utcnow()` |

- `OrderStatus` enum: `pending`, `confirmed`, `shipped`, `delivered`, `cancelled`
- **File:** `backend/app/features/orders/models.py`

### `order_items`

| Column       | Type   | Constraints       |
|--------------|--------|-------------------|
| `id`         | int    | PK, auto-increment |
| `order_id`   | int    | NOT NULL, FK → orders.id |
| `product_id` | int    | NOT NULL          |
| `quantity`   | int    | NOT NULL          |
| `unit_price` | float  | NOT NULL, default: 0.0 |

- Snapshots the price at order time (currently always 0.0 in MVP)
- **File:** `backend/app/features/orders/models.py`

---

## Indexes

| Table       | Indexed Column | Type   |
|-------------|----------------|--------|
| `users`     | `email`        | UNIQUE |
| `users`     | `email`        | B-tree (explicit `index=True`) |
| `carts`     | `user_id`      | UNIQUE |

All other FK columns (`cart_id`, `user_id`, `order_id`) implicitly benefit from PK indexes on their referenced tables. No additional explicit indexes are defined in the MVP.

---

## Migrations

Managed via **Alembic**. Migration files live in `backend/alembic/versions/`. Run:

```bash
uv run alembic upgrade head
```

To create a new migration after model changes:

```bash
uv run alembic revision --autogenerate -m "description"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/core/database.py` | Engine, session factory, `create_db_and_tables()` |
| `app/features/users/models.py` | `User` model |
| `app/features/cart/models.py` | `Cart` and `CartItem` models |
| `app/features/orders/models.py` | `Order` and `OrderItem` models |
| `app/features/orders/domain/__init__.py` | `OrderStatus` enum |
| `app/features/users/domain/__init__.py` | `UserRole` enum |
| `alembic/` | Migration scripts |
