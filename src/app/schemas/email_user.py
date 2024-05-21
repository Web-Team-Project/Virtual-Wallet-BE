from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class LoginRequest(BaseModel):
    email: str
    password: str