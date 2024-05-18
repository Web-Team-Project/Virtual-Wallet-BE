from fastapi import APIRouter, Depends
from app.schemas.card import CardCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.common.utils import process_request
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.services.crud.card import create_card, read_card, update_card, delete_card
from app.sql_app.models.models import User, Card
from uuid import UUID


router = APIRouter()


@router.post("/cards")
async def create(card: CardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _create_card() -> Card:
        return await create_card(db, card, current_user.id)

    return await process_request(_create_card)


@router.get("/cards/{card_id}")
async def read(card_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    async def _read_card():
        return await read_card(card_id, db, current_user.id)

    return await process_request(_read_card)


@router.put("/cards/{card_id}")
async def update(card_id: UUID, card: CardCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    async def _update_card():
        card.user_id = current_user.id
        return await update_card(db, card_id, card)

    return await process_request(_update_card)


@router.delete("/cards/{card_id}")
async def delete(card_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _delete_card():
        return await delete_card(db, card_id, current_user.id)

    return await process_request(_delete_card)