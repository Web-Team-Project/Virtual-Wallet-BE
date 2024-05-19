from enum import Enum


class Role(Enum):
    user = "user"
    admin = "admin"
    owner = "owner"


class Status(Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"


class Currency(Enum):
    BGN = "BGN"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    BTC = "BTC"
    ETH = "ETH"
