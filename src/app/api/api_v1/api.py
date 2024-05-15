"""REST API endpoints"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    hello_world, items
)
from app.services import auth

api_router = APIRouter()

api_router.include_router(
    hello_world.router,
    prefix="/hello-world",
    tags=["Hello World"],
)

api_router.include_router(
    auth.router,
    prefix="",
    tags=["Authentication"],
)

api_router.include_router(
    items.router,
    prefix="",
    tags=["Users"],
)