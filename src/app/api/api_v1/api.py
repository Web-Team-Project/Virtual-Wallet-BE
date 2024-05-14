"""REST API endpoints"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    hello_world, items, test_auth
)

api_router = APIRouter()

api_router.include_router(
    hello_world.router,
    prefix="/hello-world",
    tags=["Hello World"],
)

api_router.include_router(
    test_auth.router,
    prefix="",
    tags=["Hello World"],
)

api_router.include_router(
    items.router,
    prefix="",
    tags=["Users"],
)