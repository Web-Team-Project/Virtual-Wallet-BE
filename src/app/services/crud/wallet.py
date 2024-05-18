from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException, status
from app.sql_app.models.models import Wallet



async def add_money_to_wallet(db: AsyncSession, wallet_id: UUID, amount: float):
    try:
        wallet = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
        wallet = wallet.scalar_one()
        wallet.balance += amount
        await db.commit()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Wallet not found.")