from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from app.sql_app.models.enumerate import Currency, IntervalType


class TransactionBase(BaseModel):
    amount: int
    currency: Currency
    timestamp: datetime
    card_id: UUID
    sender_id: UUID
    recipient_id: UUID
    category_id: UUID
    status: str

    

class TransactionCreate(BaseModel):
    amount: float
    currency: str
    timestamp: Optional[datetime] = None
    card_number: str
    recipient_email: str
    category: str

    class Config:
        from_attributes = True

class Transaction(TransactionBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True

class Category(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
class TransactionView(BaseModel):
    id: UUID
    amount: int
    currency: str
    timestamp: datetime
    card_id: UUID
    sender_id: UUID
    recipient_id: UUID
    category_id: UUID
    status: str
    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sender_id: Optional[UUID] = None
    recipient_id: Optional[UUID] = None
    direction: Optional[str] = None
    sort_by: Optional[str] = None


class TransactionList(BaseModel):
    transactions: List[TransactionView]  # Use TransactionView instead of Transaction
    total: int


class RecurringTransactionCreate(BaseModel):
    amount: int
    currency: Currency
    card_id: UUID
    recipient_id: UUID
    category_id: UUID
    interval: Optional[int] = None
    interval_type: IntervalType
    next_execution_date: datetime
