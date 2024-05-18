from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transaction import TransactionBase, TransactionCreate
from app.schemas.user import UserBase
from app.sql_app.database import get_db
from app.sql_app.models.models import User, Transaction
from app.services.crud.transaction import create_transaction, get_transactions_by_user_id
from app.services.common.utils import process_request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.services.common.utils import get_current_user

router = APIRouter()

@router.get("/transactions")
async def get_transactions(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _get_transactions() -> List[Transaction]:
        return await get_transactions_by_user_id(db, current_user.id)

    return await process_request(_get_transactions)


@router.post("/transactions")
async def create_transaction_endpoint(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _create_transaction() -> Transaction:
        return await create_transaction(db, transaction, current_user.id)

    return await process_request(_create_transaction)


@router.post("/transactions", response_model=TransactionBase)
async def create(
    transaction: TransactionCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: UserBase = Depends(get_current_user) #current_user - user_base
):
    async def _create_transaction() -> Transaction:
        return await create_transaction(db, transaction, current_user.id, transaction.recipient_id)
    
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