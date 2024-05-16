from datetime import datetime
from pydantic import BaseModel


class TransactionBase(BaseModel):
    amount: int
    timestamp: datetime
    category: str
    is_recurring: bool
    card_id: int
    user_id: int
    category_id: int


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True