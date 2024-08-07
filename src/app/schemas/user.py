from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.card import Card
from app.schemas.category import Category
from app.schemas.contact import Contact
from app.schemas.transaction import Transaction


class UserBase(BaseModel):
    id: UUID
    sub: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    email: str
    email_verified: bool
    locale: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False
    is_admin: Optional[bool] = False


class UserCreate(UserBase):
    pass


class User(UserBase):
    cards: List[Card] = []
    categories: List[Category] = []
    contacts: List[Contact] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True


class AddPhoneRequest(BaseModel):
    phone_number: str = Field(..., min_length=13, max_length=13)


class VerifyPhoneRequest(BaseModel):
    code: str
