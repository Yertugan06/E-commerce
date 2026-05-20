from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)
    stock: int = Field(default=0, nullable=False)
