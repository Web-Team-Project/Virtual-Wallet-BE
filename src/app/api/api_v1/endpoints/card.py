from fastapi import APIRouter, Depends
from app.schemas.card import CardCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import User
from app.services.common.utils import get_current_user, process_request
from app.sql_app.database import get_db
from app.services.crud.card import create_card, read_all_cards, read_card, update_card, delete_card
from app.sql_app.models.models import Card
from uuid import UUID


router = APIRouter()


@router.post("/cards")
async def create(card: CardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new card for the user.
        Parameters:
            card (CardCreate): The card data.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Card: The created card object.
    """
    async def _create_card() -> Card:
        return await create_card(db, card, current_user.id)

    return await process_request(_create_card)


@router.get("/cards/{card_id}")
async def read(card_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    View the details of a card for the user.
        Parameters:
            card_id (UUID): The ID of the card to view.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Card: The card object.
    """
    async def _read_card():
        return await read_card(db, card_id, current_user.id)

    return await process_request(_read_card)


@router.get("/cards")
async def read_all(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    View all cards for the user.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            List[Card]: A list of card objects belonging to the user.
    """
    async def _read_all_cards():
        return await read_all_cards(db, current_user.id)

    return await process_request(_read_all_cards)


@router.put("/cards/{card_id}")
async def update(card_id: UUID, card: CardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update the details of a card for the user.
        Parameters:
            card_id (UUID): The ID of the card to update.
            card (CardCreate): The card data.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Card: The updated card object.
    """
    async def _update_card():
        return await update_card(db, card_id, card, current_user.id)

    return await process_request(_update_card)


@router.delete("/cards/{card_id}")
async def delete(card_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a card for the user.
        Parameters:
            card_id (UUID): The ID of the card to delete.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Card: The deleted card object.
    """
    async def _delete_card():
        return await delete_card(db, card_id, current_user.id)

    return await process_request(_delete_card)