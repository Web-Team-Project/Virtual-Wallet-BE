from enum import Enum


class Role(Enum):
    user = "user"
    admin = "admin"
    owner = "owner"


class Status(Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"