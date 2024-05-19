from uuid import UUID
from fastapi import APIRouter, Depends
from app.services.common.utils import get_current_user, process_request
from app.services.crud.user import block_user, deactivate_user, get_user_by_email, search_users, unblock_user, update_user_role
from app.sql_app.database import get_db
from app.sql_app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get("/users/{email}")
async def get_user(email: str, db: AsyncSession = Depends(get_db)):

    async def _get_user():
        return await get_user_by_email(email, db)
    
    return await process_request(_get_user)


@router.put("/users/{user_id}/role")
async def update_role(user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _update_user_role():
        return await update_user_role(user_id, db, current_user)
    
    return await process_request(_update_user_role)


@router.delete("/users/{user_id}/deactivate")
async def deactivate(user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _deactivate_user():
        return await deactivate_user(user_id, db, current_user)
    
    return await process_request(_deactivate_user)


@router.put("/users/{user_id}/block")
async def block(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _block_user():
        return await block_user(user_id, db, current_user)
    
    return await process_request(_block_user)


@router.put("/users/{user_id}/unblock")
async def unblock(user_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _unblock_user():
        return await unblock_user(user_id, db, current_user)
    
    return await process_request(_unblock_user)


@router.get("/search/users")
async def search_all_users(search: str, db: AsyncSession = Depends(get_db)):

    async def _search_users():
        return await search_users(search, db)
    
    return await process_request(_search_users)