from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.core.security import get_password_hash
from app.features.cart.models import Cart, CartItem
from app.features.orders.models import Order, OrderItem
from app.features.users.domain import UserRole
from app.features.users.models import User


async def seed():
    async with AsyncSession(engine) as db:
        existing = await db.execute(select(User).where(User.email == "admin@example.com"))
        if existing.scalar_one_or_none() is not None:
            print("Seed data already exists, skipping.")
            return

        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRole.ADMIN,
        )
        alice = User(
            email="alice@example.com",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CUSTOMER,
        )
        bob = User(
            email="bob@example.com",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CUSTOMER,
        )
        db.add_all([admin, alice, bob])
        await db.flush()

        alice_cart = Cart(user_id=alice.id)
        bob_cart = Cart(user_id=bob.id)
        db.add_all([alice_cart, bob_cart])
        await db.flush()

        db.add_all([
            CartItem(cart_id=alice_cart.id, product_id=101, quantity=2),
            CartItem(cart_id=alice_cart.id, product_id=102, quantity=1),
            CartItem(cart_id=bob_cart.id, product_id=201, quantity=3),
        ])

        order = Order(user_id=alice.id, total_amount=49.99)
        db.add(order)
        await db.flush()

        db.add_all([
            OrderItem(order_id=order.id, product_id=101, quantity=1, unit_price=19.99),
            OrderItem(order_id=order.id, product_id=103, quantity=2, unit_price=15.00),
        ])

        await db.commit()

    print("Seed data created: admin@example.com, alice@example.com, bob@example.com")
    print("  Admin password: Admin123!")
    print("  Customer password: Password123!")
    print("  Carts and sample order created.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed())
