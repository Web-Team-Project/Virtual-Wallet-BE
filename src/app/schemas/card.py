from datetime import datetime
from pydantic import BaseModel


class CardBase(BaseModel):
    number: str
    card_holder: str
    exp_date: datetime
    cvv: str
    design: str
    user_id: int


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int

    class Config:
        orm_mode = True