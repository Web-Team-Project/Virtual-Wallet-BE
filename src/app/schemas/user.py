from pydantic import BaseModel


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
    id: int

    class Config:
        orm_mode = True