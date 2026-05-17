from fastapi import APIRouter, status

from app.core.dependencies import CurrentUserDep, DBSessionDep
from app.features.cart.schemas import CartRead, CartItemCreate, CartItemUpdate, CartItemRead
from app.features.cart.repositories import (
    get_cart_by_user_id,
    add_item_to_cart,
    update_cart_item_quantity,
    remove_cart_item,
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartRead)
async def get_cart(user: CurrentUserDep, db: DBSessionDep):
    return await get_cart_by_user_id(db, user.id)


@router.post("/items", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
async def add_item(body: CartItemCreate, user: CurrentUserDep, db: DBSessionDep):
    return await add_item_to_cart(db, user.id, body)


@router.put("/items/{item_id}", response_model=CartItemRead)
async def update_item(item_id: int, body: CartItemUpdate, user: CurrentUserDep, db: DBSessionDep):
    return await update_cart_item_quantity(db, user.id, item_id, body)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, user: CurrentUserDep, db: DBSessionDep):
    await remove_cart_item(db, user.id, item_id)
