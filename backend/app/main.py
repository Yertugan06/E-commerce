import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

from app.core.database import create_db_and_tables
from app.core.error_handlers import (
    app_http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.core.health import health_endpoint
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
        logger.exception("Failed to create database tables during startup")
    yield


app = FastAPI(title="E-Commerce MVP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, app_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(checkout_router)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health(request: Request):
    return await health_endpoint(request)
