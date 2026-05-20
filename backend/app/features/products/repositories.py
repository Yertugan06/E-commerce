from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.models import Product
from app.features.products.schemas import ProductRead


async def get_all_products(db: AsyncSession) -> list[ProductRead]:
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()
    return [
        ProductRead(id=p.id, name=p.name, price=p.price, stock=p.stock)
        for p in products
    ]


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    return await db.get(Product, product_id)
