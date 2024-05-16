from fastapi import APIRouter, Depends
from app.schemas.card import CardCreate
from sqlalchemy.orm import Session

from app.services.common.utils import process_request
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.services.crud.card import create_card
from app.sql_app.models.models import User, Card


router = APIRouter()


@router.post("/cards")
async def create(card: CardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _create_card() -> Card:
        return await create_card(db, card, current_user.id)

    return await process_request(_create_card)


@router.get("/cards/{card_id}")
async def get_card(card_id: int):
    pass


@router.put("/cards/{card_id}")
async def update_card(card_id: int):
    pass


@router.delete("/cards/{card_id}")
async def delete_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    await _delete_card(db, card_id, current_user.id)
    return {"message": "Card deleted successfully."}