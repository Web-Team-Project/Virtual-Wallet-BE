from enum import Enum


class Status(Enum):
    pending = "pending"
    awaiting = "awaiting"
    confirmed = "confirmed"
    declined = "declined"


class Currency(Enum):
    BGN = "BGN"
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    BTC = "BTC"
    ETH = "ETH"


class IntervalType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"