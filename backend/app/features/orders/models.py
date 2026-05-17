from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.features.orders.domain import OrderStatus


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, foreign_key="users.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING, nullable=False)
    total_amount: float = Field(default=0.0, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(nullable=False, foreign_key="orders.id")
    product_id: int = Field(nullable=False)
    quantity: int = Field(nullable=False)
    unit_price: float = Field(default=0.0, nullable=False)

    order: Order = Relationship(back_populates="items")
