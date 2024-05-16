"""REST API endpoints"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth, user, card, transaction
)

api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="",
    tags=["Authentication"],
)

api_router.include_router(
    user.router,
    prefix="",
    tags=["Users"],
)

api_router.include_router(
    card.router,
    prefix="",
    tags=["Cards"],
)

api_router.include_router(
    transaction.router,
    prefix="",
    tags=["Transactions"],
)