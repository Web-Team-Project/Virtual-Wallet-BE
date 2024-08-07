from typing import List

from pydantic import BaseModel

from app.schemas.transaction import TransactionBase


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    transactions: List[TransactionBase] = []

    class Config:
        from_attributes = True
