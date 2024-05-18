from fastapi import APIRouter, Depends
from app.schemas.wallet import WalletCreate
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.services.common.utils import get_current_user, process_request
from app.services.crud.wallet import add_funds_to_wallet, withdraw_funds_from_wallet
from app.sql_app.database import get_db


router = APIRouter()


@router.post("/wallets/{user_id}/add_funds")
async def add_funds(wallet: WalletCreate, db: AsyncSession = Depends(get_db), current_user: UUID = Depends(get_current_user)):

    async def _add_funds():
        return await add_funds_to_wallet(db, wallet, current_user)
    
    return await process_request(_add_funds)


@router.post("/wallets/{user_id}/withdraw_funds")
async def withdraw_funds(wallet: WalletCreate, db: AsyncSession = Depends(get_db), current_user: UUID = Depends(get_current_user)):

    async def _withdraw_funds():
        return await withdraw_funds_from_wallet(db, wallet, current_user)

    return await process_request(_withdraw_funds)