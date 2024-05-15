from datetime import datetime
from pydantic import BaseModel, Field


class CardBase(BaseModel):
    number: str = Field(..., min_length=16, max_length=16)
    card_holder: str = Field(..., min_length=2, max_length=30)
    exp_date: datetime
    cvv: str = Field(..., min_length=3, max_length=3)
    design: str
    user_id: int


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int

    class Config:
        orm_mode = True