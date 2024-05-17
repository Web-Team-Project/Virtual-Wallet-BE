from fastapi import APIRouter, Depends
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.schemas.transaction import TransactionCreate
from app.sql_app.models.models import User, Transaction
from app.services.crud.transaction import create_transaction
from app.services.common.utils import process_request
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/transactions")
async def create(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    async def _create_transaction() -> Transaction:
        return await create_transaction(db, transaction, current_user.id)
    
    return await process_request(_create_transaction)


# @router.get("/transactions/{transaction_id}")
# async def get_transaction_(transaction_id: int,
#                            db: AsyncSession = Depends(get_db),
#                            current_user: User = Depends(get_current_user)):
#     async def _get_transaction():
#         return await get_transaction(transaction_id, db, current_user.id)
    
#     @router.get("/cards/{card_id}")
# async def read(card_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
#     async def _read_card():
#         return await read_card(card_id, db, current_user.id)

#     return await process_request(_read_card)


@router.get("/transactions")
async def get_transactions():
    pass


@router.post("/transactions/{transaction_id}/approve")
async def approve_transaction():
    pass


@router.post("/transactions/{transaction_id}/reject")
async def reject_transaction():
    pass


@router.post("/transactions/{transaction_id}/withdraw")
async def withdraw():
    pass