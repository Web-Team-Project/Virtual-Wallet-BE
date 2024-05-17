from sqlalchemy import Date, create_engine
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.sql_app.database import Base
from app.sql_app.models.role import Role
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    sub = Column(String, unique=True, index=True)
    name = Column(String)
    given_name = Column(String)
    family_name = Column(String)
    picture = Column(String)
    email = Column(String, unique=True, index=True)
    email_verified = Column(Boolean)
    locale = Column(String)
    role = Column(Enum(Role), default="user")
    cards = relationship("Card", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    number = Column(String, unique=True, index=True)
    card_holder = Column(String)
    exp_date = Column(Date)
    cvv = Column(String)
    design = Column(String) # Image url
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = Column(Integer)
    timestamp = Column(DateTime(timezone=True))
    category = Column(String)
    is_recurring = Column(Boolean)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))

    card = relationship("Card", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True)

    transactions = relationship("Transaction", back_populates="category")


SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/virtual-wallet-db"
sync_engine = create_engine(SYNC_DATABASE_URL)
Base.metadata.create_all(bind=sync_engine)