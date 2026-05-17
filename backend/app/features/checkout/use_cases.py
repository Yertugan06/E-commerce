from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CART_EMPTY, RESOURCE_NOT_FOUND
from app.features.cart.models import CartItem
from app.features.cart.repositories import ensure_cart_exists
from app.features.checkout.payment import process_payment
from app.features.orders.models import OrderItem
from app.features.orders.repositories import create_order_from_cart, get_orders_by_user_id, get_order_by_id
from app.features.orders.schemas import OrderRead, OrderItemRead, OrderListRead


DEFAULT_UNIT_PRICE = 19.99


async def _get_cart_items(db: AsyncSession, cart_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
    return list(result.scalars().all())


async def _get_order_items(db: AsyncSession, order_id: int) -> list[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


async def checkout(db: AsyncSession, user_id: int) -> OrderRead:
    cart = await ensure_cart_exists(db, user_id)
    items = await _get_cart_items(db, cart.id)

    if not items:
        raise CART_EMPTY()

    cart_item_tuples = [
        (item.product_id, item.quantity, DEFAULT_UNIT_PRICE) for item in items
    ]
    total = sum(qty * DEFAULT_UNIT_PRICE for _, qty, price in cart_item_tuples)

    process_payment(total)

    order = await create_order_from_cart(db, user_id, cart_item_tuples, total)

    order_id = order.id
    order_user_id = order.user_id
    order_status = order.status
    order_total = order.total_amount
    order_created_at = order.created_at

    for item in items:
        await db.delete(item)
    await db.commit()

    order_items = await _get_order_items(db, order_id)

    return OrderRead(
        id=order_id,
        user_id=order_user_id,
        status=order_status,
        total_amount=order_total,
        created_at=order_created_at,
        items=[
            OrderItemRead(
                id=oi.id,
                order_id=oi.order_id,
                product_id=oi.product_id,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
            )
            for oi in order_items
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
        raise RESOURCE_NOT_FOUND("Order not found")

    order_items = await _get_order_items(db, order.id)

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
            for oi in order_items
        ],
    )
