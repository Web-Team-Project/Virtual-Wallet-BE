from datetime import datetime
from pydantic import BaseModel


class TransactionBase(BaseModel):
    amount: int
    timestamp: datetime
    category: str
    card_id: int
    user_id: int


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True