from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CardBase(BaseModel):
    number: str = Field(..., min_length=16, max_length=16)
    card_holder: str = Field(..., min_length=2, max_length=30)
    exp_date: str = Field(..., pattern=r"^(0[1-9]|1[0-2])\/\d{2}$")
    cvv: str = Field(..., min_length=3, max_length=3)
    design: str

    @field_validator("exp_date")
    def validate_exp_date(cls, v):
        try:
            datetime.strptime(v, "%m/%y")
        except ValueError:
            raise ValueError("Expiration date must be in MM/YY format.")
        return v


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: UUID

    class Config:
        from_attributes = True
