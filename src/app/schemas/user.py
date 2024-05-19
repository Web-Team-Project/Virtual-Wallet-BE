from typing import List, Optional
from pydantic import BaseModel
from app.schemas.transaction import Transaction
from app.schemas.card import Card
from uuid import UUID


class UserBase(BaseModel):
    id: UUID
    sub: str
    name: str
    given_name: str
    family_name: str
    picture: str
    email: str
    email_verified: bool
    locale: str
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False
    is_admin: Optional[bool] = False


class UserCreate(UserBase):
    pass


class User(UserBase):
    cards: List[Card] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True