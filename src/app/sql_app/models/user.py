from app.sql_app.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sub = Column(String, unique=True, index=True)
    name = Column(String)
    given_name = Column(String)
    family_name = Column(String)
    picture = Column(String)
    email = Column(String, unique=True, index=True)
    email_verified = Column(Boolean)
    locale = Column(String)

    # cards = relationship("Card", back_populates="user")
    # transactions = relationship("Transaction", back_populates="user")