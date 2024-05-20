from pydantic import BaseModel
from uuid import UUID
from app.sql_app.models.enumerate import Currency


class WalletBase(BaseModel):
    user_id: UUID
    amount: float = 0.0
    currency: Currency


class WalletCreate(BaseModel):
    amount: float = 0.0
    currency: Currency


class Wallet(WalletBase):
    id: UUID

    class Config:
        from_attributes = True

class WalletWithdraw(BaseModel):
    amount: float
    currency: Currency