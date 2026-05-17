from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.database import create_db_and_tables
from app.core.error_handlers import (
    app_http_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.features.auth.router import router as auth_router
from app.features.cart.router import router as cart_router
from app.features.checkout.router import router as checkout_router
from app.features.users.models import User
from app.features.cart.models import Cart, CartItem
from app.features.orders.models import Order, OrderItem


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        await create_db_and_tables()
    except Exception:
        pass
    yield


app = FastAPI(title="E-Commerce MVP", version="0.1.0", lifespan=lifespan)

app.add_exception_handler(HTTPException, app_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(checkout_router)


@app.get("/")
async def root():
    return {"status": "ok"}
