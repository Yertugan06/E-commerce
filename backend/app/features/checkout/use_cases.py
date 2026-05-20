import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CART_EMPTY, RESOURCE_NOT_FOUND, AppHTTPException
from app.core.metrics import track_checkout, track_checkout_duration
from app.core.sli_checks import validate_order_persistence
from app.features.cart.models import Cart, CartItem
from app.features.checkout.payment import process_payment
from app.features.orders.domain import OrderStatus
from app.features.orders.models import OrderItem
from app.features.orders.repositories import create_order_from_cart, get_orders_by_user_id, get_order_by_id
from app.features.orders.schemas import OrderRead, OrderItemRead, OrderListRead
from app.features.products.models import Product

logger = logging.getLogger(__name__)


async def _get_cart_items(db: AsyncSession, cart_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
    return list(result.scalars().all())


async def _get_order_items(db: AsyncSession, order_id: int) -> list[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


@track_checkout_duration
async def checkout(db: AsyncSession, user_id: int) -> OrderRead:
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalar_one_or_none()
    if cart is None:
        track_checkout("cart_empty")
        raise CART_EMPTY()
    items = await _get_cart_items(db, cart.id)

    if not items:
        logger.warning("Checkout failed: cart empty for user_id=%s", user_id)
        track_checkout("cart_empty")
        raise CART_EMPTY()

    product_ids = [item.product_id for item in items]
    result = await db.execute(select(Product).where(Product.id.in_(product_ids)).with_for_update())
    products = {p.id: p for p in result.scalars().all()}

    for item in items:
        product = products.get(item.product_id)
        if product is None:
            raise RESOURCE_NOT_FOUND(f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            track_checkout("stock_insufficient")
            raise AppHTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}' (requested {item.quantity}, available {product.stock})",
                error_code="INSUFFICIENT_STOCK",
            )

    cart_item_tuples = [
        (item.product_id, item.quantity, products[item.product_id].price, products[item.product_id].name)
        for item in items
    ]
    total = sum(qty * price for _, qty, price, _ in cart_item_tuples)

    payment_success = await process_payment(total)
    if not payment_success:
        logger.warning("Checkout failed: payment declined for user_id=%s total=%.2f", user_id, total)
        track_checkout("payment_failed")
        raise AppHTTPException(
            status_code=402,
            detail="Payment failed",
            error_code="PAYMENT_FAILED",
        )

    order = await create_order_from_cart(db, user_id, cart_item_tuples, total)
    order.status = OrderStatus.CONFIRMED

    order_id = order.id
    order_user_id = order.user_id
    order_status = order.status
    order_total = order.total_amount
    order_created_at = order.created_at

    for item in items:
        product = products[item.product_id]
        product.stock -= item.quantity
    await db.flush()

    for item in items:
        await db.delete(item)
    await db.commit()

    order_items = await _get_order_items(db, order_id)

    await validate_order_persistence(db, order_id, user_id)

    track_checkout("success")
    logger.info("Checkout succeeded: user_id=%s order_id=%s total=%.2f", user_id, order_id, order_total)

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
                product_name=oi.product_name,
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
                product_name=oi.product_name,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
            )
            for oi in order_items
        ],
    )
