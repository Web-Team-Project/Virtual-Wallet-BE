from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionList
from app.sql_app.models.models import Transaction, Wallet, User, Card
from app.sql_app.models.enumerate import Status
from uuid import UUID
import uuid


async def create_transaction(db: AsyncSession, transaction_data: TransactionCreate, sender_id: UUID) -> Transaction:
    sender_result = await db.execute(select(User).where(User.id == sender_id))
    sender = sender_result.scalars().first()
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Sender not found.")
    if sender.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Sender is blocked.")
    
    sender_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == sender_id))
    sender_wallet = sender_wallet_result.scalars().first()
    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sender's wallet not found.")
    if sender_wallet.balance < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Insufficient funds.")

    card_result = await db.execute(select(Card).where(Card.id == transaction_data.card_id, Card.user_id == sender_id))
    card = card_result.scalars().first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")

    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction_data.recipient_id))
    recipient_wallet = recipient_wallet_result.scalars().first()
    if not recipient_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipient's wallet not found.")

    new_transaction = Transaction(id=uuid.uuid4(),
                                  amount=transaction_data.amount,
                                  currency=transaction_data.currency,
                                  timestamp=transaction_data.timestamp,
                                  card_id=transaction_data.card_id,
                                  sender_id=sender_id,
                                  recipient_id=transaction_data.recipient_id,
                                  category_id=transaction_data.category_id,
                                  wallet_id=sender_wallet.id,
                                  status="pending")
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction


async def confirm_transaction(transaction_id: UUID, db: AsyncSession, current_user: User) -> Transaction:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalars().first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Transaction not found.")
    if transaction.status == "confirmed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Transaction is already confirmed.")
    transaction.status = "awaiting"
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def get_transactions_by_user_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Transaction).where(Transaction.sender_id == user_id))
    return result.scalars().all()


async def get_transactions(db: AsyncSession, current_user: User, filter: TransactionFilter, skip: int, limit: int) -> TransactionList:
    if current_user.is_admin:
        query = select(Transaction)
    else:
        query = select(Transaction).where(or_(Transaction.sender_id == current_user.id, Transaction.recipient_id == current_user.id))

    if filter.start_date:
        query = query.where(Transaction.timestamp >= filter.start_date)
    if filter.end_date:
        query = query.where(Transaction.timestamp <= filter.end_date)
    if filter.sender_id:
        query = query.where(Transaction.sender_id == filter.sender_id)
    if filter.recipient_id:
        query = query.where(Transaction.recipient_id == filter.recipient_id)
    if filter.direction:
        if filter.direction == "incoming":
            query = query.where(Transaction.recipient_id == current_user.id)
        elif filter.direction == "outgoing":
            query = query.where(Transaction.sender_id == current_user.id)

    if filter.sort_by:
        if filter.sort_by == "amount":
            query = query.order_by(Transaction.amount)
        elif filter.sort_by == "date":
            query = query.order_by(Transaction.timestamp)

    total = await db.execute(query.with_only_columns(func.count()))
    transactions = await db.execute(query.offset(skip).limit(limit))
    return TransactionList(transactions=transactions.scalars().all(), total=total.scalar())


async def approve_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: UUID) -> Transaction:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalars().first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Transaction with id {transaction_id} not found.")
    if transaction.recipient_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to approve this transaction.")
    if transaction.status != Status.awaiting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can only approve transactions that are awaiting your approval.")
    sender_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction.sender_id))
    sender_wallet = sender_wallet_result.scalars().first()
    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == transaction.recipient_id))
    recipient_wallet = recipient_wallet_result.scalars().first()
    if sender_wallet.balance < transaction.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Insufficient funds.")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Transaction with id {transaction_id} not found.")
    if transaction.recipient_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to reject this transaction.")
    if transaction.status != Status.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can only reject pending transactions.")
    transaction.status = Status.declined
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def deny_transaction(db: AsyncSession, current_user: User, transaction_id: UUID):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Only admins can deny transactions.")
    transaction = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = transaction.scalars().first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Transaction not found.")
    if transaction.status != "pending" or transaction.status != "awaiting":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Transaction is not pending or awaiting.")
    await db.execute(update(Transaction).where(Transaction.id == transaction_id).values(status="declined"))
    await db.commit()
    return {"message": "Transaction declined."}