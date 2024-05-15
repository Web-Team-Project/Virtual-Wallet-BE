from fastapi import APIRouter, Depends
from app.services.crud.user import get_current_user, update_user_role as _update_user_role
from app.sql_app.database import get_db
from app.sql_app.models.user import User
from sqlalchemy.orm import Session


router = APIRouter()


router.put("users/{user_id}/role")
async def update_user_role(user_id: int, role: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await _update_user_role(user_id, role, db, current_user)
    