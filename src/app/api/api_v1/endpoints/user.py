from fastapi import APIRouter, Depends
from app.services.common.utils import process_request
from app.services.crud.user import get_current_user, update_user_role
from app.sql_app.database import get_db
from app.sql_app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


router.put("/users/{user_id}/role")
async def update_role(user_id: int, role: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _update_user_role():
        return await update_user_role(user_id, role, db, current_user)
    
    return await process_request(_update_user_role)