from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.sql_app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    card_holder = Column(String)
    exp_date = Column(DateTime)
    cvv = Column(String)
    design = Column(String) # Image url
    user_id = Column(Integer, ForeignKey("users.id"))

    # user = relationship("User", back_populates="cards")