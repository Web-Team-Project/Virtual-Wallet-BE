from app.sql_app.database import Base
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sub = Column(String, unique=True)
    name = Column(String)
    given_name = Column(String)
    family_name = Column(String)
    picture = Column(String)
    email = Column(String, unique=True)
    email_verified = Column(Boolean)
    locale = Column(String)