"""REST API endpoints"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth_google, user, card, transaction, category, contact, wallet, auth_mail
)

api_router = APIRouter()


api_router.include_router(
    auth_google.router,
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

api_router.include_router(
    category.router,
    prefix="",
    tags=["Category"]
)

api_router.include_router(
    contact.router,
    prefix="",
    tags=["Contacts"],
)

api_router.include_router(
    wallet.router,
    prefix="",
    tags=["Wallets"],
)

api_router.include_router(
    auth_mail.router,
    prefix="",
    tags=["E-mail authentication"]
)