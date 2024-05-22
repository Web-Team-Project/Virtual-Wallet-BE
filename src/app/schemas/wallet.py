from pydantic import BaseModel
from uuid import UUID
from app.sql_app.models.enumerate import Currency


class WalletBase(BaseModel):
    currency: Currency


class WalletCreate(BaseModel):
    amount: float = 0.0
    currency: Currency


class Wallet(WalletBase):
    id: UUID
    amount: float = 0.0

    class Config:
        from_attributes = True