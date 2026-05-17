from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.orders.models import Order, OrderItem


async def create_order_from_cart(
    db: AsyncSession, user_id: int, cart_items: list[tuple[int, int, float]], total_amount: float = 0.0
) -> Order:
    order = Order(user_id=user_id, total_amount=total_amount)
    db.add(order)
    await db.flush()

    for product_id, quantity, unit_price in cart_items:
        item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        db.add(item)

    await db.flush()
    return order


async def get_orders_by_user_id(db: AsyncSession, user_id: int) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def get_order_by_id(db: AsyncSession, order_id: int, user_id: int) -> Order | None:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    return result.scalar_one_or_none()
