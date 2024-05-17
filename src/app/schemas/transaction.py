from datetime import datetime
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

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: UUID

    class Config:
        from_attributes = True