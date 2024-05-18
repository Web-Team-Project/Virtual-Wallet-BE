from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.schemas.wallet import WalletCreate
from app.sql_app.models.models import Wallet



async def add_funds_to_wallet(db: AsyncSession, wallet: WalletCreate, user_id: UUID):
    db_wallet = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    db_wallet = db_wallet.scalars().first()
    if db_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Wallet not found.")
    db_wallet.balance += wallet.amount
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet


async def withdraw_funds_from_wallet(db: AsyncSession, wallet: WalletCreate, user_id: UUID):
    db_wallet = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    db_wallet = db_wallet.scalars().first()
    if db_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Wallet not found.")
    if db_wallet.balance < wallet.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Insufficient funds.")
    db_wallet.balance -= wallet.amount
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet