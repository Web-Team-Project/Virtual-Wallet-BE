from fastapi import APIRouter, Depends
from app.schemas.wallet import WalletBase, WalletCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.common.utils import get_current_user, process_request
from app.services.crud.wallet import add_funds_to_wallet, check_balance, create_wallet, withdraw_funds_from_wallet
from app.sql_app.database import get_db
from app.schemas.user import User


router = APIRouter()


@router.post("/wallet/")
async def create_wallet_endpoint(wallet_create: WalletBase, db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    async def _create_wallet():
        return await create_wallet(db, current_user.id, wallet_create.currency)

    return await process_request(_create_wallet)


@router.post("/wallets/{user_id}/add")
async def add_funds(wallet: WalletCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _add_funds():
        return await add_funds_to_wallet(db, wallet.amount, current_user, wallet.currency)

    return await process_request(_add_funds)


@router.post("/wallets/withdraw")
async def withdraw_funds(wallet: WalletCreate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):

    async def _withdraw_funds():
        return await withdraw_funds_from_wallet(db, current_user, wallet.amount, wallet.currency)

    return await process_request(_withdraw_funds)


@router.get("/wallets/balance")
async def get_balance(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _get_balance():
        return await check_balance(db, current_user)

    return await process_request(_get_balance)
