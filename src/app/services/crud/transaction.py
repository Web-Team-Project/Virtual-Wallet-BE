from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionCreate, TransactionBase
from app.sql_app.models.models import Category, Transaction
from uuid import UUID

async def create_transaction(db: AsyncSession, transaction: TransactionCreate, user_id: UUID) -> Transaction:
    result = await db.execute(select(Category).where(Category.id == transaction.category_id))
    category = result.scalars().first()
    
    if category is None:
        raise ValueError(f"Category with id {transaction.category_id} not found")

    db_transaction = Transaction(
        amount=transaction.amount,
        timestamp=transaction.timestamp,
        is_recurring=transaction.is_recurring,
        card_id=transaction.card_id,
        user_id=user_id,
        category_id=category.id
    )

    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction



 
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