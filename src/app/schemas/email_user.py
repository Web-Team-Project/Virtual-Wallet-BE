from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.schemas.card import Card
from app.schemas.category import Category
from app.schemas.contact import Contact
from app.schemas.transaction import Transaction


class EmailUserBase(BaseModel):
    given_name: str
    family_name: str
    email: EmailStr
    hashed_password: str = Field(..., min_length=8)


class EmailUserCreate(EmailUserBase):
    pass


class EmailUser(EmailUserBase):
    id: UUID
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False
    is_admin: Optional[bool] = False
    cards: List[Card] = []
    categories: List[Category] = []
    contacts: List[Contact] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str