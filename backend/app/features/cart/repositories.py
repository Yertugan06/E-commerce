from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RESOURCE_CONFLICT, RESOURCE_NOT_FOUND
from app.core.sli_checks import validate_cart_consistency
from app.features.cart.models import Cart, CartItem
from app.features.cart.schemas import CartItemCreate, CartItemUpdate, CartRead, CartItemRead
from app.features.products.models import Product


async def ensure_cart_exists(db: AsyncSession, user_id: int) -> Cart:
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        if cart.id is None:
            raise RuntimeError("Cart ID was not assigned after refresh")
    return cart


async def _load_cart_items(db: AsyncSession, cart_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
    return list(result.scalars().all())


async def _item_to_read(db: AsyncSession, item: CartItem) -> CartItemRead:
    product = await db.get(Product, item.product_id)
    return CartItemRead(
        id=item.id,
        cart_id=item.cart_id,
        product_id=item.product_id,
        product_name=product.name if product else "",
        quantity=item.quantity,
        unit_price=product.price if product else 0.0,
    )


async def get_cart_by_user_id(db: AsyncSession, user_id: int) -> CartRead:
    cart = await ensure_cart_exists(db, user_id)
    items = await _load_cart_items(db, cart.id)
    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=[await _item_to_read(db, item) for item in items],
    )


async def add_item_to_cart(
    db: AsyncSession, user_id: int, body: CartItemCreate
) -> CartItemRead:
    product = await db.get(Product, body.product_id)
    if product is None:
        raise RESOURCE_NOT_FOUND(f"Product {body.product_id} not found")
    if product.stock < 1:
        raise RESOURCE_CONFLICT(f"Product '{product.name}' is out of stock")
    if body.quantity > product.stock:
        raise RESOURCE_CONFLICT(
            f"Insufficient stock for '{product.name}' (requested {body.quantity}, available {product.stock})"
        )

    cart = await ensure_cart_exists(db, user_id)
    items = await _load_cart_items(db, cart.id)

    for existing in items:
        if existing.product_id == body.product_id:
            raise RESOURCE_CONFLICT("Product already in cart")

    expected_count = len(items) + 1
    expected_ids = {it.product_id for it in items} | {body.product_id}

    item = CartItem(cart_id=cart.id, product_id=body.product_id, quantity=body.quantity)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    await validate_cart_consistency(
        db, user_id,
        expected_item_count=expected_count,
        expected_product_ids=expected_ids,
    )
    return await _item_to_read(db, item)


async def update_cart_item_quantity(
    db: AsyncSession, user_id: int, item_id: int, body: CartItemUpdate
) -> CartItemRead:
    cart = await ensure_cart_exists(db, user_id)
    item = await db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise RESOURCE_NOT_FOUND("Item not found")

    result = await db.execute(
        select(Product).where(Product.id == item.product_id).with_for_update()
    )
    product = result.scalar_one_or_none()
    if product is not None and body.quantity > product.stock + item.quantity:
        raise RESOURCE_CONFLICT(
            f"Insufficient stock for '{product.name}' (requested {body.quantity}, available {product.stock}, already in cart {item.quantity})"
        )

    item.quantity = body.quantity
    await db.commit()
    await db.refresh(item)
    await validate_cart_consistency(db, user_id)
    return await _item_to_read(db, item)


async def remove_cart_item(db: AsyncSession, user_id: int, item_id: int) -> None:
    cart = await ensure_cart_exists(db, user_id)
    item = await db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise RESOURCE_NOT_FOUND("Item not found")

    await db.delete(item)
    await db.commit()
    await validate_cart_consistency(db, user_id)

