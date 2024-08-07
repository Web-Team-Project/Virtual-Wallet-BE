from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.card import CardCreate
from app.sql_app.models.models import Card


async def create_card(db: AsyncSession, card: CardCreate, user_id: UUID):
    """
    Create a new card for the user. It checks if card with the same number already exists.
        Parameters:
            db (AsyncSession): The database session.
            card (CardCreate): The card data.
            user_id (UUID): The ID of the user.
        Returns:
            Card: The created card object.
    """
    result = await db.execute(select(Card).filter_by(number=card.number))
    existing_card = result.scalar_one_or_none()
    if existing_card is not None:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Card with id {card.number} is taken.",
        )
    db_card = Card(
        number=card.number,
        card_holder=card.card_holder,
        exp_date=card.exp_date,
        cvv=card.cvv,
        design=card.design,
        user_id=user_id,
    )
    db.add(db_card)
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def read_card(db: AsyncSession, card_id: UUID, user_id: UUID):
    """
    View card's details by id.
        Parameters:
            db (AsyncSession): The database session.
            card_id (UUID): The ID of the card.
            user_id (UUID): The ID of the user.
        Returns:
            Card: The card object.
    """
    result = await db.execute(
        select(Card).where(Card.id == card_id, Card.user_id == user_id)
    )
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id {card_id} not found for user {user_id}.",
        )
    return db_card


async def read_all_cards(db: AsyncSession, user_id: UUID):
    """
    Retrieve all cards belonging to a user.
        Parameters:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user.
        Returns:
            List[Card]: A list of card objects belonging to the user.
    """
    result = await db.execute(select(Card).where(Card.user_id == user_id))
    return result.scalars().all()


async def update_card(db: AsyncSession, card_id: UUID, card: CardCreate, user_id: UUID):
    """
    Update card's details by id.
        Parameters:
            db (AsyncSession): The database session.
            card_id (UUID): The ID of the card.
            card (CardCreate): The card data.
            user_id (UUID): The ID of the user.
        Returns:
            Card: The updated card object.
    """
    result = await db.execute(
        select(Card).where(Card.id == card_id), Card.user_id == user_id
    )
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found."
        )
    db_card.number = card.number
    db_card.card_holder = card.card_holder
    db_card.exp_date = card.exp_date
    db_card.cvv = card.cvv
    db_card.design = card.design
    await db.commit()
    await db.refresh(db_card)
    return db_card


async def delete_card(db: AsyncSession, card_id: UUID, user_id: UUID):
    """
    Delete card by id.
        Parameters:
            db (AsyncSession): The database session.
            card_id (UUID): The ID of the card.
            user_id (UUID): The ID of the user.
        Returns:
            dict: A message confirming the deletion.
    """
    result = await db.execute(
        select(Card).where(and_(Card.id == card_id, Card.user_id == user_id))
    )
    db_card = result.scalars().first()
    if db_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found."
        )
    await db.delete(db_card)
    await db.commit()
    return {"message": "Card deleted successfully."}
