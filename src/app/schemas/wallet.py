from pydantic import BaseModel
from uuid import UUID


class WalletBase(BaseModel):
    user_id: UUID
    amount: float = 0.0


class WalletCreate(WalletBase):
    id: UUID


class Wallet(WalletBase):
    id: UUID

    class Config:
        from_attributes = True