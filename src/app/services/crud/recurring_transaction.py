import calendar
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import RecurringTransactionCreate, TransactionCreate
from app.services.crud.transaction import create_transaction
from app.sql_app.models.enumerate import IntervalType
from app.sql_app.models.models import  RecurringTransaction, Transaction, Card, User, Wallet, Category
from uuid import UUID
import uuid
import pytz


async def create_recurring_transaction(db: AsyncSession, transaction_data: RecurringTransactionCreate, sender_id: UUID) -> Transaction:
    """
    Create a new recurring transaction for the user. It will be executed at the specified interval.
        Parameters:
            db (AsyncSession): The database session.
            transaction_data (RecurringTransactionCreate): The recurring transaction data.
            sender_id (UUID): The ID of the sender.
        Returns:
            RecurringTransaction: The created recurring transaction object.
    """
    sender_result = await db.execute(select(User).where(User.id == sender_id))
    sender = sender_result.scalars().first()
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Sender not found.")
    if sender.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Sender is blocked.")
    
    sender_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == sender_id, Wallet.currency == transaction_data.currency))
    sender_wallet = sender_wallet_result.scalars().first()

    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sender's wallet in the specified currency not found.")
    if sender_wallet.balance < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Insufficient funds.")

    card_result = await db.execute(select(Card).where(Card.id == transaction_data.card_id, Card.user_id == sender_id))
    card = card_result.scalars().first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")

    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction_data.recipient_id, Wallet.currency == transaction_data.currency))
    recipient_wallet = recipient_wallet_result.scalars().first()
    if not recipient_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipient's wallet not found.")

    if sender_wallet.currency != recipient_wallet.currency:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Sender's and recipient's wallets must be in the same currency.")

    new_transaction = RecurringTransaction(id=uuid.uuid4(),
                                           currency=transaction_data.currency,
                                           user_id=sender_id,
                                           card_id=transaction_data.card_id,
                                           recipient_id=transaction_data.recipient_id,
                                           category_id=transaction_data.category_id,
                                           amount=transaction_data.amount,
                                           interval=transaction_data.interval,
                                           interval_type=transaction_data.interval_type,
                                           next_execution_date=transaction_data.next_execution_date) 
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction


async def process_recurring_transactions(db: AsyncSession):
    """
    Process any recurring transactions that are due for payment.
        Parameters:
            db (AsyncSession): The database session.
        """
    current_time = datetime.now(pytz.utc)
    result = await db.execute(select(RecurringTransaction).where(and_(RecurringTransaction.next_execution_date <= current_time)))
    due_recurring_transactions = result.scalars().all()
    for recurring_transaction in due_recurring_transactions:

        card_result = await db.execute(select(Card).where(Card.id == recurring_transaction.card_id))
        card = card_result.scalars().first()
        recipient_result = await db.execute(select(User).where(User.id == recurring_transaction.recipient_id))
        recipient = recipient_result.scalars().first()
        category_result = await db.execute(select(Category).where(Category.id == recurring_transaction.category_id))
        category = category_result.scalars().first()

        transaction_data = TransactionCreate(amount=recurring_transaction.amount,
                                             currency=recurring_transaction.currency,
                                             timestamp=datetime.now(pytz.utc),
                                             card_number=card.number,
                                             recipient_email=recipient.email,
                                             category=category.name
        )
        try:
            await create_transaction(db, transaction_data, recurring_transaction.user_id)
            if recurring_transaction.interval_type == IntervalType.DAILY:
                recurring_transaction.next_execution_date += timedelta(days=1)
            elif recurring_transaction.interval_type == IntervalType.WEEKLY:
                recurring_transaction.next_execution_date += timedelta(weeks=1)
            elif recurring_transaction.interval_type == IntervalType.MONTHLY:
                next_month = recurring_transaction.next_execution_date.month % 12 + 1
                next_year = recurring_transaction.next_execution_date.year + \
                            (recurring_transaction.next_execution_date.month // 12)
                last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
                day = min(recurring_transaction.next_execution_date.day, last_day_of_next_month)
                recurring_transaction.next_execution_date = recurring_transaction.next_execution_date.replace(
                    month=next_month, year=next_year, day=day)
            db.add(recurring_transaction)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        

async def get_recurring_transactions(db: AsyncSession, current_user: User):
    """
    Get all recurring transactions set by the user.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            List[RecurringTransaction]: The list of recurring transactions.
    """
    result = await db.execute(select(RecurringTransaction).where(RecurringTransaction.user_id == current_user.id))
    return result.scalars().all()


async def cancel_recurring_transaction(db: AsyncSession, recurring_transaction_id: UUID, user_id: UUID):
    """
    Cancel a recurring transaction.
        Parameters:
            db (AsyncSession): The database session.
            recurring_transaction_id (UUID): The ID of the recurring transaction to be cancelled.
            user_id (UUID): The ID of the user.
        Returns:
            RecurringTransaction: The cancelled recurring transaction object.
    """
    result = await db.execute(select(RecurringTransaction).where(RecurringTransaction.id == recurring_transaction_id))
    recurring_transaction = result.scalars().first()
    if not recurring_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Recurring transaction not found.")
    current_user_id = UUID(str(user_id))
    if recurring_transaction.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User does not have permission to cancel this recurring transaction.")
    await db.delete(recurring_transaction)
    await db.commit()
    return recurring_transaction