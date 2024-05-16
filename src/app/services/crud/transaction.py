from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.transaction import TransactionCreate
from app.sql_app.models.models import Transaction


async def create_transaction(db: Session, transaction: TransactionCreate, user_id: int):
    db_transaction = Transaction(amount=transaction.amount,
                                    timestamp=transaction.timestamp,
                                    category=transaction.category,
                                    is_reccuring=transaction.is_reccuring,
                                    card_id=transaction.card_id,
                                    user_id=user_id,
                                    category_id=transaction.category_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
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