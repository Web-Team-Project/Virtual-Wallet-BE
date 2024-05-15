from sqlalchemy import Column, Integer
from app.sql_app.database import Base
from enum import Enum
from sqlalchemy.orm import relationship


class RoleEnum(Enum):
    user = "user"
    admin = "admin"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Enum(RoleEnum), unique=True)

    users = relationship("User", back_populates="role")