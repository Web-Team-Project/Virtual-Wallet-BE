from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transaction import TransactionBase, TransactionCreate
from app.schemas.user import UserBase
from app.sql_app.database import get_db
from app.schemas.user import User
from app.schemas.transaction import Transaction
from app.services.crud.transaction import confirm_transaction, create_transaction, get_transactions_by_user_id, approve_transaction, reject_transaction
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


@router.post("/transaction")
async def create_transaction_endpoint(transaction: TransactionCreate, db: AsyncSession = Depends(get_db),
                                      current_user: User = Depends(get_current_user)):

    async def _create_transaction() -> Transaction:
        return await create_transaction(db, transaction, current_user.id)

    return await process_request(_create_transaction)


@router.put("/transactions/{transaction_id}/confirm")
async def confirm_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    async def _confirm_transaction() -> Transaction:
        return await confirm_transaction(db, transaction_id, current_user.id)

    return await process_request(_confirm_transaction)


@router.post("/transaction/{transaction_id}/approve")
async def approve_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    async def _approve_transaction() -> Transaction:
        return await approve_transaction(db, transaction_id, current_user.id)

    return await process_request(_approve_transaction)


@router.post("/transaction/{transaction_id}/reject")
async def reject_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    async def _reject_transaction() -> Transaction:
        return await reject_transaction(db, transaction_id, current_user.id)
    
    return await process_request(_reject_transaction)