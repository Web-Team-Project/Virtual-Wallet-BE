from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.transaction import RecurringTransactionCreate
from app.schemas.user import User
from app.services.common.utils import get_current_user, process_request
from app.services.crud.recurring_transaction import (
    cancel_recurring_transaction,
    create_recurring_transaction,
    get_recurring_transactions,
)
from app.sql_app.database import get_db

router = APIRouter()


@router.post("/recurring_transactions")
async def create_recurring_transaction_endpoint(
    recurring_transaction: RecurringTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new recurring transaction for the user.
    The recurring transaction will be used to create transactions at a regular interval.
        Parameters:
            recurring_transaction (RecurringTransactionCreate): The recurring transaction data.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            RecurringTransaction: The created recurring transaction object.
    """

    async def _create_recurring_transaction():
        return await create_recurring_transaction(
            db, recurring_transaction, current_user.id
        )

    return await process_request(_create_recurring_transaction)


@router.get("/recurring_transactions")
async def get_recurring_transactions_endpoint(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all recurring transactions set by the user.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            List[RecurringTransaction]: The list of recurring transactions.
    """

    async def _get_recurring_transactions():
        return await get_recurring_transactions(db, current_user)

    return await process_request(_get_recurring_transactions)


@router.delete("/recurring_transactions/cancel")
async def cancel_recurring_transaction_endpoint(
    recurring_transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a recurring transaction set by the user.
        Parameters:
            recurring_transaction_id (str): The ID of the recurring transaction to cancel.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the cancellation.
    """

    async def _cancel_recurring_transaction():
        return await cancel_recurring_transaction(
            db, recurring_transaction_id, current_user.id
        )

    return await process_request(_cancel_recurring_transaction)
