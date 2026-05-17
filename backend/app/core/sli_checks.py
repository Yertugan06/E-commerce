import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.metrics import order_persistence_validations_total, cart_consistency_validations_total
from app.features.orders.repositories import get_order_by_id

logger = logging.getLogger(__name__)


async def validate_order_persistence(db: AsyncSession, order_id: int, user_id: int) -> bool:
    if not settings.SLI_ENABLED:
        return True

    try:
        order = await get_order_by_id(db, order_id, user_id)
        if order is not None:
            order_persistence_validations_total.labels(status="success").inc()
            return True
        order_persistence_validations_total.labels(status="failure").inc()
        logger.warning("Order persistence validation failed: order_id=%s user_id=%s not readable after write", order_id, user_id)
        return False
    except Exception as exc:
        order_persistence_validations_total.labels(status="failure").inc()
        logger.error("Order persistence validation error: order_id=%s user_id=%s error=%s", order_id, user_id, exc)
        return False


async def validate_cart_consistency(
    db: AsyncSession,
    user_id: int,
    expected_item_count: int | None = None,
    expected_product_ids: set[int] | None = None,
) -> bool:
    if not settings.SLI_ENABLED:
        return True

    try:
        from app.features.cart.repositories import get_cart_by_user_id
        cart = await get_cart_by_user_id(db, user_id)

        actual_ids = {item.product_id for item in cart.items}
        ok = True

        if expected_item_count is not None and len(cart.items) != expected_item_count:
            ok = False

        if expected_product_ids is not None and actual_ids != expected_product_ids:
            ok = False

        if ok:
            cart_consistency_validations_total.labels(status="success").inc()
        else:
            cart_consistency_validations_total.labels(status="failure").inc()
            logger.warning(
                "Cart consistency validation failed: user_id=%s expected_count=%s expected_products=%s actual=%s",
                user_id, expected_item_count, expected_product_ids, actual_ids,
            )

        return ok
    except Exception as exc:
        cart_consistency_validations_total.labels(status="failure").inc()
        logger.error("Cart consistency validation error: user_id=%s error=%s", user_id, exc)
        return False
