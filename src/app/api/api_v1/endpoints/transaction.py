from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transaction import TransactionCreate
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.sql_app.models.models import User, Transaction
from app.services.crud.transaction import create_transaction
from app.services.common.utils import process_request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

router = APIRouter()



@router.post("/transactions")
async def create(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    async def _create_transaction() -> Transaction:
        return await create_transaction(db, transaction, current_user.id)
    
    return await process_request(_create_transaction)

@router.post("/transactions/{transaction_id}/approve")
async def approve_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    async def _approve_transaction() -> Transaction:
        result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()

        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} not found")

        transaction.status = "approved"  # Change status to approved
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    return await process_request(_approve_transaction)

@router.post("/transactions/{transaction_id}/reject")
async def reject_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    async def _reject_transaction() -> Transaction:
        result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()

        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} not found")

        transaction.status = "rejected"  # Change status to rejected
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    return await process_request(_reject_transaction)


@router.post("/transactions/{transaction_id}/withdraw")
async def withdraw():
    pass