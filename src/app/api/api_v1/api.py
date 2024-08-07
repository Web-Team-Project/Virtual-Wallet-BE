"""REST API endpoints"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth_email,
    auth_google,
    card,
    category,
    contact,
    recurring_transaction,
    transaction,
    user,
    wallet,
)

api_router = APIRouter()


api_router.include_router(
    auth_google.router,
    prefix="",
    tags=["Authentication"],
)

api_router.include_router(
    auth_email.router,
    prefix="",
    tags=["Email Authentication"],
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
    recurring_transaction.router, prefix="", tags=["Recurring Transactions"]
)

api_router.include_router(category.router, prefix="", tags=["Category"])

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
