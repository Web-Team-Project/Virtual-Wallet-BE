from typing import List
from fastapi import APIRouter, Depends
from app.schemas.transaction import TransactionCreate, TransactionFilter
from app.sql_app.database import get_db
from app.schemas.user import User
from app.schemas.transaction import Transaction
from app.services.crud.transaction import confirm_transaction, create_transaction, deny_transaction, get_transactions, approve_transaction, reject_transaction
from app.services.common.utils import process_request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.services.common.utils import get_current_user


router = APIRouter()


@router.get("/transactions")
async def view_transactions(filter: TransactionFilter = Depends(), 
                            skip: int = 0, 
                            limit: int = 100, 
                            db: AsyncSession = Depends(get_db), 
                            current_user: User = Depends(get_current_user)):
    
    async def _get_transactions() -> List[Transaction]:
        return await get_transactions(db, current_user, filter, skip, limit)

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
        return await confirm_transaction(transaction_id, db, current_user)

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


@router.put("/transaction/{transaction_id}/deny")
async def deny_transaction_endpoint(transaction_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _deny_transaction() -> Transaction:
        return await deny_transaction(db, transaction_id, current_user.id)

    return await process_request(_deny_transaction)