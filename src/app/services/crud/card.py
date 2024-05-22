from fastapi import HTTPException, status
from app.schemas.card import CardCreate
from app.sql_app.models.models import Card
from app.schemas.user import User
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID


async def create_card(db: AsyncSession, card: CardCreate, user_id: UUID):
    result = await db.execute(select(Card).filter_by(number=card.number))
    existing_card = result.scalar_one_or_none()
    if existing_card is not None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, 
                            detail=f"Card with id {card.number} is taken.")
    db_card = Card(number=card.number, 
                   card_holder=card.card_holder, 
                   exp_date=card.exp_date, 
                   cvv=card.cvv, 
                   design=card.design, 
                   user_id=user_id)
    

    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def read_card(db: AsyncSession, card_id: UUID, user_id: UUID):
    result = await db.execute(select(Card).where(Card.id == card_id, Card.user_id == user_id))
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Card with id {card_id} not found for user {user_id}.")
    return db_card


async def update_card(db: AsyncSession, card_id: UUID, card: CardCreate, user_id: UUID):
    result = await db.execute(select(Card).where(Card.id == card_id), Card.user_id == user_id)
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Card not found.")
    db_card.number = card.number
    db_card.card_holder = card.card_holder
    db_card.exp_date = card.exp_date
    db_card.cvv = card.cvv
    db_card.design = card.design
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def delete_card(db: AsyncSession, card_id: UUID, user_id: UUID):
    result = await db.execute(select(Card).where(and_(Card.id == card_id, Card.user_id == user_id)))
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Card not found.")
    await db.delete(db_card)
    await db.commit()
    return {"message": "Card deleted successfully."}