from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.sql_app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True)

    transactions = relationship("Transaction", back_populates="category")