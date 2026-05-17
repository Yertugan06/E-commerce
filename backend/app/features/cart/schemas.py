from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemRead(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int


class CartRead(BaseModel):
    id: int
    user_id: int
    items: list[CartItemRead]
