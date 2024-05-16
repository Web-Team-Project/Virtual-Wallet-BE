from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.card import CardCreate
from app.sql_app.models.models import Card


async def create_card(db: Session, card: CardCreate, user_id: int):
    db_card = Card(number=card.number, 
                   card_holder=card.card_holder, 
                   exp_date=card.exp_date, 
                   cvv=card.cvv, 
                   design=card.design, 
                   user_id=user_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


async def read_card(db: Session, card_id: int):
    db_card = db.query(Card).filter(Card.id == card_id).first()
    if db_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Card not found.")
    return db_card


async def update_card(db: Session, card_id: int, card: CardCreate, user_id: int):
    db_card = db.query(Card).filter(Card.id == card_id, Card.user_id == user_id).first()
    if not db_card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Card not found.")
    db_card.number = card.number
    db_card.card_holder = card.card_holder
    db_card.exp_date = card.exp_date
    db_card.cvv = card.cvv
    db_card.design = card.design
    db.commit()
    db.refresh(db_card)
    return db_card


async def delete_card(db: Session, card_id: int, user_id: int):
    db_card = db.query(Card).filter(Card.id == card_id, Card.user_id == user_id).first()
    if db_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Card not found.")
    db.delete(db_card)
    db.commit()
    return db_card