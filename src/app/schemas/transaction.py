from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class TransactionBase(BaseModel):
    amount: int
    timestamp: datetime
    category: str
    is_recurring: bool
    card_id: UUID
    user_id: UUID
    category_id: UUID
    status: str


class TransactionCreate(BaseModel):
    amount: int
    timestamp: datetime
    is_recurring: bool
    card_id: UUID
    recipient_id: UUID
    category_id: UUID


class Transaction(TransactionBase):
    id: UUID

    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    sender_id: Optional[UUID]
    recipient_id: Optional[UUID]
    direction: Optional[str]
    sort_by: Optional[str]


class TransactionList(BaseModel):
    transactions: List[Transaction]
    total: int