from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.cart.repositories import ensure_cart_exists, remove_cart_item
from app.features.checkout.payment import process_payment
from app.features.orders.repositories import create_order_from_cart, get_orders_by_user_id, get_order_by_id
from app.features.orders.schemas import OrderRead, OrderItemRead, OrderListRead


async def checkout(db: AsyncSession, user_id: int) -> OrderRead:
    cart = await ensure_cart_exists(db, user_id)
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    cart_items = [(item.product_id, item.quantity) for item in cart.items]
    total = 0.0

    process_payment(total)

    order = await create_order_from_cart(db, user_id, cart_items)

    for item in list(cart.items):
        await db.delete(item)
    await db.commit()

    return OrderRead(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=[
            OrderItemRead(
                id=oi.id,
                order_id=oi.order_id,
                product_id=oi.product_id,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
            )
            for oi in order.items
        ],
    )


async def get_user_orders(db: AsyncSession, user_id: int) -> list[OrderListRead]:
    orders = await get_orders_by_user_id(db, user_id)
    return [
        OrderListRead(
            id=o.id,
            user_id=o.user_id,
            status=o.status,
            total_amount=o.total_amount,
            created_at=o.created_at,
        )
        for o in orders
    ]


async def get_order_detail(db: AsyncSession, user_id: int, order_id: int) -> OrderRead:
    order = await get_order_by_id(db, order_id, user_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return OrderRead(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=[
            OrderItemRead(
                id=oi.id,
                order_id=oi.order_id,
                product_id=oi.product_id,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
            )
            for oi in order.items
        ],
    )
