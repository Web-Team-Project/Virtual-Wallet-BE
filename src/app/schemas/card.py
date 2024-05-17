from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class CardBase(BaseModel):
    number: str = Field(..., min_length=16, max_length=16)
    card_holder: str = Field(..., min_length=2, max_length=30)
    exp_date: date
    cvv: str = Field(..., min_length=3, max_length=3)
    design: str
    user_id: UUID


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: UUID

    class Config:
        from_attributes = True