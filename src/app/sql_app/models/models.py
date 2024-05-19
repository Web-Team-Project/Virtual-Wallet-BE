from sqlalchemy import Date, create_engine
from sqlalchemy import Column, DateTime, ForeignKey, Float, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.sql_app.database import Base
from app.sql_app.models.enumerate import Status, Currency
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
    email_verified = Column(Boolean) #ako gmaial verified, facebook,
    locale = Column(String)
    phone_number = Column(String)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)


    cards = relationship("Card", back_populates="user")
    sent_transactions = relationship("Transaction", back_populates="sender", foreign_keys="[Transaction.sender_id]")
    received_transactions = relationship("Transaction", back_populates="recipient", foreign_keys="[Transaction.recipient_id]")
    contacts = relationship("Contact", back_populates="user", foreign_keys="[Contact.user_id]")
    categories = relationship("Category", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")

class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    number = Column(String)
    card_holder = Column(String)
    exp_date = Column(Date)
    cvv = Column(String)
    design = Column(String)
    is_credit = Column(Boolean)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card", foreign_keys="[Transaction.card_id]")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = Column(Float)
    timestamp = Column(DateTime(timezone=True))
    category = Column(String)
    is_recurring = Column(Boolean, default=False)
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
    amount = Column(Float, nullable=False)
    interval = Column(String, nullable=False)
    next_execution_date = Column(Date, nullable=False)

    user = relationship("User")
    card = relationship("Card")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(Enum(Currency))

    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", foreign_keys="[Transaction.wallet_id]")


SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/virtual-wallet-db"
sync_engine = create_engine(SYNC_DATABASE_URL)

Base.metadata.create_all(bind=sync_engine)