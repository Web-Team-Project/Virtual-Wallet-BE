from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.schemas.card import Card
from app.schemas.transaction import Transaction


class UserEmailSchema(BaseModel):
    email: EmailStr
    hashed_password: str = Field(..., min_length=8)
    phone_number: str = Field(..., min_length=10, max_length=10)


class UserEmailCreate(UserEmailSchema):
    pass


class UserSchema(UserEmailSchema):
    id: UUID
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False
    is_admin: Optional[bool] = False
    cards: List[Card] = []
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True


class User(BaseModel):
    username: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class LoginRequest(BaseModel):
    email: str
    password: str