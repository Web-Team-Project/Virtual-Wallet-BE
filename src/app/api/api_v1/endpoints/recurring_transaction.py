from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate
from app.schemas.user import User
from app.services.common.utils import get_current_user, process_request
from app.services.crud.recurring_transaction import create_recurring_transaction, process_recurring_transactions
from app.sql_app.database import get_db


router = APIRouter()


@router.post("/recurring_transaction")
async def create_recurring_transaction_endpoint(recurring_transaction: TransactionCreate, 
                                                db: AsyncSession = Depends(get_db), 
                                                current_user: User = Depends(get_current_user)):
    async def _create_recurring_transaction():
        return await create_recurring_transaction(db, recurring_transaction, current_user.id)

    return await process_request(_create_recurring_transaction)


@router.put("/recurring_transaction/process")
async def process_recurring_transactions_endpoint(db: AsyncSession = Depends(get_db)):
    async def _process_recurring_transactions():
        return await process_recurring_transactions(db)

    return await process_request(_process_recurring_transactions)


