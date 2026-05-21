from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.core.security import get_password_hash
from app.features.cart.models import Cart, CartItem
from app.features.orders.models import Order, OrderItem
from app.features.products.models import Product
from app.features.users.domain import UserRole
from app.features.users.models import User


PRODUCT_SEEDS = [
    Product(name="Wireless Mouse", price=29.99, stock=100000),
    Product(name="Mechanical Keyboard", price=89.99, stock=100000),
    Product(name="USB-C Hub", price=34.99, stock=100000),
    Product(name='27" Monitor', price=299.99, stock=100000),
    Product(name="Webcam 1080p", price=59.99, stock=100000),
    Product(name="Desk Lamp", price=24.99, stock=100000),
    Product(name="Noise Canceling Headphones", price=149.99, stock=100000),
    Product(name="Laptop Stand", price=39.99, stock=100000),
]


async def seed():
    async with AsyncSession(engine) as db:
        existing = await db.execute(select(User).where(User.email == "admin@example.com"))
        if existing.scalar_one_or_none() is not None:
            # Reset stock and clear stale data so load tests work on re-run.
            for p in PRODUCT_SEEDS:
                await db.execute(
                    Product.__table__.update()
                    .where(Product.name == p.name)
                    .values(stock=p.stock)
                )
            await db.execute(CartItem.__table__.delete())
            await db.execute(Cart.__table__.delete())
            await db.execute(OrderItem.__table__.delete())
            await db.execute(Order.__table__.delete())
            await db.commit()
            print("Seed data refreshed: stock reset, carts and orders cleared.")
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
        await db.refresh(alice)
        await db.refresh(bob)

        products = list(PRODUCT_SEEDS)
        db.add_all(products)
        await db.flush()
        for p in products:
            await db.refresh(p)

        alice_cart = Cart(user_id=alice.id)
        bob_cart = Cart(user_id=bob.id)
        db.add_all([alice_cart, bob_cart])
        await db.flush()
        await db.refresh(alice_cart)
        await db.refresh(bob_cart)

        db.add_all([
            CartItem(cart_id=alice_cart.id, product_id=products[0].id, quantity=2),
            CartItem(cart_id=alice_cart.id, product_id=products[1].id, quantity=1),
            CartItem(cart_id=bob_cart.id, product_id=products[2].id, quantity=3),
        ])

        order = Order(user_id=alice.id, total_amount=149.97)
        db.add(order)
        await db.flush()
        await db.refresh(order)

        db.add_all([
            OrderItem(order_id=order.id, product_id=products[0].id, quantity=1, unit_price=29.99),
            OrderItem(order_id=order.id, product_id=products[3].id, quantity=1, unit_price=299.99),
        ])

        await db.commit()

    print("Seed data created: admin@example.com, alice@example.com, bob@example.com")
    print("  Admin password: Admin123!")
    print("  Customer password: Password123!")
    print("  Carts and sample order created.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed())
