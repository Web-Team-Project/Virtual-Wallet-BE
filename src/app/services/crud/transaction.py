import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate, TransactionBase
from app.sql_app.models.models import Category, Transaction
from uuid import UUID

async def create_transaction(db: AsyncSession, transaction_data: TransactionCreate, sender_id: UUID) -> Transaction:
    new_transaction = Transaction(
        id=uuid.uuid4(),
        amount=transaction_data.amount,
        timestamp=transaction_data.timestamp,
        is_recurring=transaction_data.is_recurring,
        card_id=transaction_data.card_id,
        sender_id=sender_id,
        recipient_id=transaction_data.recipient_id,
        category_id=transaction_data.category_id,
        status="pending"  # Assuming "pending" is the default status
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction


async def get_transactions_by_user_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(Transaction).where(Transaction.sender_id == user_id))
    return result.scalars().all()

# async def read_card(db: AsyncSession, card_id: int):
#     stmt = select(Card).where(Card.id == card_id)
#     result = await db.execute(stmt)
#     db_card = result.scalars().first()
#     if db_card is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail="Card not found.")
#     return db_card


# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)
#     amount = Column(Integer)
#     timestamp = Column(DateTime(timezone=True))
#     category = Column(String)
#     is_reccuring = Column(Boolean)
#     card_id = Column(Integer, ForeignKey("cards.id"))
#     user_id = Column(Integer, ForeignKey("users.id"))
#     category_id = Column(Integer, ForeignKey("categories.id"))

#     card = relationship("Card", back_populates="transactions")
#     user = relationship("User", back_populates="transactions")
#     category = relationship("Category", back_populates="transactions")