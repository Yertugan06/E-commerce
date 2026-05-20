from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint


class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(unique=True, nullable=False, foreign_key="users.id")

    items: list["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_item_product"),)

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(nullable=False, foreign_key="carts.id")
    product_id: int = Field(nullable=False, foreign_key="products.id")
    quantity: int = Field(default=1, nullable=False)

    cart: Cart = Relationship(back_populates="items")
