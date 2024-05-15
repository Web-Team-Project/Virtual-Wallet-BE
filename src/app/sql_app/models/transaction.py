from app.sql_app.database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    timestamp = Column(DateTime(timezone=True))
    category = Column(String)
    is_reccuring = Column(Boolean)
    card_id = Column(Integer, ForeignKey("cards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    card = relationship("Card", back_populates="transactions")
    user = relationship("User", back_populates="transactions")