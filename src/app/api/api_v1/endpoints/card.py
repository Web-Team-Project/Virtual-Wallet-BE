from fastapi import APIRouter, Depends
from app.schemas.card import CardCreate
from sqlalchemy.orm import Session
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.services.crud.card import create_card as _create_card, delete_card as _delete_card


router = APIRouter()


@router.post("/cards")
async def create_card(card: CardCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return await _create_card(db, card, current_user.id)


@router.delete("/cards/{card_id}")
async def delete_card(card_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    await _delete_card(db, card_id, current_user.id)
    return {"message": "Card deleted successfully."}