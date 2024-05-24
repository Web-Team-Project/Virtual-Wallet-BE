import asyncio
from sqlalchemy import Column, DateTime, ForeignKey, Float, String, Boolean, Enum, Integer, create_engine
from sqlalchemy.orm import relationship
from app.sql_app.database import Base
from app.sql_app.models.enumerate import Status, Currency, IntervalType
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.config import get_settings
from app.sql_app.database import engine


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    sub = Column(String, unique=True, index=True)
    name = Column(String)
    given_name = Column(String)
    family_name = Column(String)
    picture = Column(String)
    email = Column(String, unique=True, index=True)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    hashed_password = Column(String)
    locale = Column(String)
    phone_number = Column(String, unique=True, index=True)
    phone_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    cards = relationship("Card", back_populates="user")
    sent_transactions = relationship("Transaction", back_populates="sender", foreign_keys="[Transaction.sender_id]")
    received_transactions = relationship("Transaction", back_populates="recipient", foreign_keys="[Transaction.recipient_id]")
    contacts = relationship("Contact", back_populates="user", foreign_keys="[Contact.user_id]")
    categories = relationship("Category", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    recurring_transactions = relationship("RecurringTransaction", back_populates="user", foreign_keys="[RecurringTransaction.user_id]")
    recurring_received_transactions = relationship("RecurringTransaction", back_populates="recipient", foreign_keys="[RecurringTransaction.recipient_id]")


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    number = Column(String, unique=True)
    card_holder = Column(String)
    exp_date = Column(String)
    cvv = Column(String)
    design = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card", foreign_keys="[Transaction.card_id]")
    recurring_transactions = relationship("RecurringTransaction", foreign_keys="[RecurringTransaction.card_id]", back_populates="card")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = Column(Float)
    currency = Column(Enum(Currency), default="BGN")
    timestamp = Column(DateTime(timezone=True))
    category = Column(String)
    status = Column(Enum(Status), default="pending")
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)

    card = relationship("Card", back_populates="transactions")
    sender = relationship("User", back_populates="sent_transactions", foreign_keys=[sender_id])
    recipient = relationship("User", back_populates="received_transactions", foreign_keys=[recipient_id])
    category = relationship("Category", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_contact_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="contacts", foreign_keys=[user_id])
    user_contact = relationship("User", back_populates="contacts", foreign_keys=[user_contact_id])


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    interval = Column(Integer, nullable=True)
    interval_type = Column(Enum(IntervalType), nullable=False)
    next_execution_date = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="recurring_transactions", foreign_keys=[user_id])
    card = relationship("Card", back_populates="recurring_transactions", foreign_keys=[card_id])
    recipient = relationship("User", back_populates="recurring_received_transactions", foreign_keys=[recipient_id])
    category = relationship("Category")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(Enum(Currency))

    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", foreign_keys="[Transaction.wallet_id]")

settings = get_settings()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)