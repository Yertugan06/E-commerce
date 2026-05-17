import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.error_handlers import (
    app_http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.core.middleware import SLIMiddleware
from app.core.health import health_endpoint
from app.core.metrics import metrics_endpoint, db_connections_active
from app.core.database import get_active_connection_count
from app.core.metrics_aggregator import aggregate_health_dashboard
from app.core.system_metrics import collect_process_metrics
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
    if settings.SLI_ENABLED:
        logger.info("SLI monitoring enabled")
    yield


app = FastAPI(title="E-Commerce MVP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.SLI_ENABLED:
    app.add_middleware(SLIMiddleware)

app.add_exception_handler(HTTPException, app_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(checkout_router)


@app.get("/")
async def root():
    return {"status": "ok"}


if settings.SLI_ENABLED:

    @app.get("/health")
    async def health(request: Request):
        return await health_endpoint(request)

    @app.get("/metrics")
    async def metrics():
        collect_process_metrics()

        try:
            count = await get_active_connection_count()
            db_connections_active.set(count)
        except Exception:
            logger.warning("Failed to collect DB connection count")

        return await metrics_endpoint()

