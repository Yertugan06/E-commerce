from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.cart.models import Cart, CartItem
from app.features.cart.schemas import CartItemCreate, CartItemUpdate, CartRead, CartItemRead


async def ensure_cart_exists(db: AsyncSession, user_id: int) -> Cart:
    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items))
    )
    cart = result.scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        cart.items = []
    return cart


async def get_cart_by_user_id(db: AsyncSession, user_id: int) -> CartRead:
    cart = await ensure_cart_exists(db, user_id)
    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemRead(id=item.id, cart_id=item.cart_id, product_id=item.product_id, quantity=item.quantity)
            for item in cart.items
        ],
    )


async def add_item_to_cart(
    db: AsyncSession, user_id: int, body: CartItemCreate
) -> CartItemRead:
    cart = await ensure_cart_exists(db, user_id)

    for existing in cart.items:
        if existing.product_id == body.product_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product already in cart",
            )

    item = CartItem(cart_id=cart.id, product_id=body.product_id, quantity=body.quantity)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CartItemRead(id=item.id, cart_id=item.cart_id, product_id=item.product_id, quantity=item.quantity)


async def update_cart_item_quantity(
    db: AsyncSession, user_id: int, item_id: int, body: CartItemUpdate
) -> CartItemRead:
    cart = await ensure_cart_exists(db, user_id)
    item = await db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    item.quantity = body.quantity
    await db.commit()
    await db.refresh(item)
    return CartItemRead(id=item.id, cart_id=item.cart_id, product_id=item.product_id, quantity=item.quantity)


async def remove_cart_item(db: AsyncSession, user_id: int, item_id: int) -> None:
    cart = await ensure_cart_exists(db, user_id)
    item = await db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    await db.delete(item)
    await db.commit()
