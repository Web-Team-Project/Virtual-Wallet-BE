import uuid
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.schemas.wallet import WalletCreate, WalletWithdraw
from app.sql_app.models.models import Wallet
from app.sql_app.models.enumerate import Currency


async def create_wallet(db: AsyncSession, user_id: UUID, currency: Currency) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency))
    wallet = result.scalars().first()

    if wallet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail ="Wallet already exists for this user and currency")

    new_wallet =Wallet(
        id=uuid.uuid4(),
        user_id=user_id,
        balance=0.0,
        currency=currency
    )
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)

    return new_wallet


# async def add_funds_to_wallet(db: AsyncSession, wallet: WalletCreate, user_id: UUID):
#     db_wallet = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
#     db_wallet = db_wallet.scalars().first()
#     if db_wallet is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="Wallet not found.")
#     db_wallet.balance += wallet.amount
#     await db.commit()
#     await db.refresh(db_wallet)
#     return db_wallet


async def withdraw_funds_from_wallet(db: AsyncSession, user_id: UUID, amount: float, currency: Currency) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency))
    wallet = result.scalars().first()
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Wallet not found.")
    if wallet.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Insufficient funds.")
    wallet.balance -= amount
    await db.commit()
    await db.refresh(wallet)
    return wallet
