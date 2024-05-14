from typing import List
from pydantic import BaseModel
from app.sql_app.models import Cards, Transactions

# da razdelim
class CardBase(BaseModel):
    number: str
    card_holder: str
    exp_date: str
    cvv: str
    design: str


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    id: int
    amount: int
    timestamp: str
    category: str
    card_id: int
    user_id: int


class TransactionCreate(Transactions):
    pass


class Transaction(TransactionBase):
    id: int
    timestamp: str
    category: str
    card_id: int
    user_id: int
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    contact_number: str
    is_active: bool
    is_admin: bool
    photo: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str
    cards: List[Card] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str