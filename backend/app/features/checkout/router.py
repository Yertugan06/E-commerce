from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBSessionDep
from app.features.checkout.use_cases import checkout, get_user_orders, get_order_detail
from app.features.orders.schemas import OrderRead, OrderListRead

router = APIRouter(tags=["checkout"])


@router.post("/checkout", response_model=OrderRead)
async def create_checkout(user: CurrentUserDep, db: DBSessionDep):
    return await checkout(db, user.id)


@router.get("/orders", response_model=list[OrderListRead])
async def list_orders(user: CurrentUserDep, db: DBSessionDep):
    return await get_user_orders(db, user.id)


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, user: CurrentUserDep, db: DBSessionDep):
    return await get_order_detail(db, user.id, order_id)
