from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionList, TransactionView
from app.sql_app.models.models import Category, Transaction, Wallet, User, Card
from app.sql_app.models.enumerate import Status
from uuid import UUID
import uuid
from sqlalchemy.orm import joinedload
from sqlalchemy import select


async def create_transaction(db: AsyncSession, transaction_data: TransactionCreate, sender_id: UUID) -> Transaction:
    """
    Create a transaction to send money from one user's wallet to another user's wallet.
        Parameters:
            db (AsyncSession): The database session.
            transaction_data (TransactionCreate): The transaction data.
            sender_id (UUID): The ID of the sender.
        Returns:
            Transaction: The created transaction object.
    """

    sender_result = await db.execute(select(User).where(User.id == sender_id))
    sender = sender_result.scalars().first()
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sender not found.")
    if sender.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sender is blocked.")

    sender_wallet_result = await db.execute(
        select(Wallet).where(Wallet.user_id == sender_id, Wallet.currency == transaction_data.currency))
    sender_wallet = sender_wallet_result.scalars().first()
    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sender's wallet in the specified currency not found.")
    if sender_wallet.balance < transaction_data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Insufficient funds.")

    card_result = await db.execute(
        select(Card).where(Card.number == transaction_data.card_number, Card.user_id == sender_id))
    card = card_result.scalars().first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")

    recipient_result = await db.execute(select(User).where(User.email == transaction_data.recipient_email))
    recipient = recipient_result.scalars().first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipient not found.")
    
    category_result = await db.execute(select(Category).where(Category.name == transaction_data.category))
    category = category_result.scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Category not found.")

    recipient_wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == recipient.id))
    recipient_wallet = recipient_wallet_result.scalars().first()
    if not recipient_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipient's wallet not found.")

    if sender_wallet.currency != recipient_wallet.currency:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Sender's and recipient's wallets must be in the same currency.")

    date_time = datetime.now()
    new_transaction = Transaction(id=uuid.uuid4(),
                                  amount=transaction_data.amount,
                                  currency=transaction_data.currency,
                                  timestamp=date_time,
                                  card_id=card.id,
                                  sender_id=sender_id,
                                  recipient_id=recipient.id,
                                  category_id=category.id,
                                  wallet_id=sender_wallet.id,
                                  status="pending")
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    transaction_result = TransactionCreate(amount=transaction_data.amount,
                                  currency=transaction_data.currency,
                                  timestamp=date_time,
                                  card_number=card.number,
                                  recipient_email=recipient.email,
                                  category=category.name,)
    return transaction_result


async def confirm_transaction(transaction_id: UUID, db: AsyncSession, current_user_id: str) -> Transaction:
    """
    Confirm a transaction by the sender so that the recipient can approve it.
        Parameters:
            transaction_id (UUID): The ID of the transaction.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Transaction: The updated transaction object.
    """
    current_user_id = UUID(current_user_id)

    async with db.begin():
        result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()

        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Transaction with id {transaction_id} not found.")

        sender_id = UUID(str(transaction.sender_id))

        if sender_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not allowed to confirm this transaction.")

        if transaction.status != Status.pending:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You can only confirm transactions that are pending your confirmation.")

    transaction.status = Status.awaiting
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def get_transactions_by_user_id(db: AsyncSession, user_id: UUID):
    """
    Get all transactions made by a user with the given user_id.
        Parameters:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user.
        Returns:
            List[Transaction]: A list of transactions made by the user.
    """
    result = await db.execute(select(Transaction).where(Transaction.sender_id == user_id))
    return result.scalars().all()


async def get_transactions(db: AsyncSession, current_user: User, filter: TransactionFilter, skip: int, limit: int):
    """
       Retrieve transactions based on the provided filters and pagination parameters.

       Parameters:
           db (AsyncSession): The database session.
           current_user (User): The current user requesting the transactions.
           filter (TransactionFilter): The filters to apply to the transaction query.
           skip (int): The number of transactions to skip for pagination.
           limit (int): The maximum number of transactions to return.

       Returns:
           TransactionList: A list of transactions matching the filters and pagination parameters, along with the total count.
       """
    query = select(Transaction).options(
        joinedload(Transaction.card),
        joinedload(Transaction.category),
        joinedload(Transaction.recipient)
    )

    if not current_user.is_admin:
        query = query.where(
            (Transaction.sender_id == current_user.id) |
            (Transaction.recipient_id == current_user.id)
        )

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

    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    transactions_result = await db.execute(query.offset(skip).limit(limit))
    transactions = transactions_result.scalars().all()

    transactions_data = []
    for transaction in transactions:
        transaction_view = TransactionView(
            id=transaction.id,
            amount=transaction.amount,
            currency=transaction.currency.name,
            timestamp=transaction.timestamp,
            card_id=transaction.card_id,
            sender_id=transaction.sender_id,
            recipient_id=transaction.recipient_id,
            category_id=transaction.category_id,
            status=transaction.status.name,
            card_number=transaction.card.number,
            recipient_email=transaction.recipient.email,
            category_name=transaction.category.name
        )
        transactions_data.append(transaction_view)

    return TransactionList(transactions=transactions_data, total=total)




async def approve_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: str) -> Transaction:
    """
    Approve an incoming transaction by the recipient.
        Parameters:
            db (AsyncSession): The database session.
            transaction_id (UUID): The ID of the transaction.
            current_user_id (str): The ID of the current user as a string.
        Returns:
            Transaction: The updated transaction object.
    """
    current_user_id = UUID(current_user_id)

    async with db.begin():
        result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Transaction with id {transaction_id} not found.")
        
        recipient_id = UUID(str(transaction.recipient_id))

        if recipient_id != current_user_id:
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


async def reject_transaction(db: AsyncSession, transaction_id: UUID, current_user_id: str) -> Transaction:
    """
    Reject an incoming transaction by the recipient.
        Parameters:
            db (AsyncSession): The database session.
            transaction_id (UUID): The ID of the transaction.
            current_user_id (str): The ID of the current user as a string.
        Returns:
            Transaction: The updated transaction object.
    """
    current_user_id = UUID(current_user_id)

    async with db.begin():
        result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Transaction with id {transaction_id} not found.")

        if transaction.recipient_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not allowed to reject this transaction.")
        
        if transaction.status != Status.awaiting:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You can only reject awaiting transactions.")

        transaction.status = Status.declined

        await db.commit()

        await db.refresh(transaction)
        
        return transaction


async def deny_transaction(db: AsyncSession, current_user: User, transaction_id: UUID):
    """
    Deny a certain transaction by the admin.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
            transaction_id (UUID): The ID of the transaction.
        Returns:
            dict: A dictionary with the message that the transaction has been denied.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Only admins can deny transactions.")
    transaction = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = transaction.scalars().first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Transaction not found.")
    if (transaction.status != Status.pending) and (transaction.status != Status.awaiting):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Transaction is not pending or awaiting.")
    await db.execute(update(Transaction).where(Transaction.id == transaction_id).values(status="declined"))
    await db.commit()
    return {"message": "Transaction declined."}
