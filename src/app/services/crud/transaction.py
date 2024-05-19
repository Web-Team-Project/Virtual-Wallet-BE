import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate
from app.sql_app.models.models import  Transaction, Wallet
from app.sql_app.models.enumerate import Status
from uuid import UUID

async def create_transaction(db: AsyncSession, transaction_data: TransactionCreate, sender_id: UUID) -> Transaction:
    sender_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == sender_id))
    sender_wallet = sender_wallet_result.scalars().first()

    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender's wallet not found")

    if sender_wallet.balance < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction_data.recipient_id))
    recipient_wallet = recipient_wallet_result.scalars().first()
    if not recipient_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient's wallet not found")

    new_transaction = Transaction(
        id=uuid.uuid4(),
        amount=transaction_data.amount,
        timestamp=transaction_data.timestamp,
        is_recurring=transaction_data.is_recurring,
        card_id=transaction_data.card_id,
        sender_id=sender_id,
        recipient_id=transaction_data.recipient_id,
        category_id=transaction_data.category_id,
        status="pending"
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction


async def get_transactions_by_user_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Transaction).where(Transaction.sender_id == user_id))
    return result.scalars().all()


async def approve_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: UUID) -> Transaction:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Transaction with id {transaction_id} not found")

    if transaction.recipient_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if transaction.status != Status.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    sender_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction.sender_id))
    sender_wallet = sender_wallet_result.scalars().first()
    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction.recipient_id))
    recipient_wallet = recipient_wallet_result.scalars().first()

    if sender_wallet.balance < transaction.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    sender_wallet.balance -= transaction.amount
    recipient_wallet.balance += transaction.amount

    transaction.status = Status.confirmed
    db.add(transaction)
    db.add(sender_wallet)
    db.add(recipient_wallet)
    await db.commit()
    await db.refresh(transaction)
    await db.refresh(sender_wallet)
    await db.refresh(recipient_wallet)
    return transaction


async def reject_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: UUID) -> Transaction:

    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {transaction_id} not found")

    if transaction.recipient_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if transaction.status != Status.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    transaction.status = Status.declined
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction

# async def withdraw_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: UUID) -> Transaction:
#     result = await db.execute(select(Transaction).where(Transaction.id) == transaction_id)
#     transaction = result.scalars().first()
#
#     if not transaction:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Transaction with id {transaction_id} not found")
#
#     if transaction.sender_id != current_user_id:
