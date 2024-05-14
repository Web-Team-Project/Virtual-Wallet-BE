from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

# da napravim papka models i v neq user.py cards.py i tn
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    contact_number = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False) # Probably roles as in the previous project
    photo = Column(String) # Image url
    cards = relationship("Cards", back_populates="user")
    transactions = relationship("Transactions", back_populates="user")


class Cards(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    card_holder = Column(String)
    exp_date = Column(DateTime)
    cvv = Column(String)
    design = Column(String) # Image url
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="cards")


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    timestamp = Column(DateTime)
    category = Column(String)
    card_id = Column(Integer, ForeignKey("cards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    card = relationship("Cards", back_populates="transactions")
    user = relationship("User", back_populates="transactions")