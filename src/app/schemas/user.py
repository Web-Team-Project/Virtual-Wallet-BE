from typing import List
from pydantic import BaseModel
from app.schemas.transaction import Transaction
from app.schemas.card import Card
from uuid import UUID


class UserBase(BaseModel):
    sub: str
    name: str
    given_name: str
    family_name: str
    picture: str
    email: str
    email_verified: bool
    locale: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    cards: List[Card] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True