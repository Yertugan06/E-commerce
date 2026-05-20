from fastapi import APIRouter

from app.core.dependencies import DBSessionDep
from app.features.products.repositories import get_all_products
from app.features.products.schemas import ProductRead

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
async def list_products(db: DBSessionDep):
    return await get_all_products(db)
