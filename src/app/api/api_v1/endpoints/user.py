from uuid import UUID
from fastapi import APIRouter, Depends
from app.services.common.utils import get_current_user, process_request
from app.services.crud.user import block_user, delete_user, get_user_by_email, search_users, unblock_user, update_user_role
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


@router.delete("/users/{email}")
async def delete(email: str, db: AsyncSession = Depends(get_db)):

    async def _delete_user():
        return await delete_user(email, db)
    
    return await process_request(_delete_user)


@router.put("/users/{email}/block")
async def block(email: str, db: AsyncSession = Depends(get_db)):

    async def _block_user():
        return await block_user(email, db)
    
    return await process_request(_block_user)


@router.put("/users/{email}/unblock")
async def unblock(email: str, db: AsyncSession = Depends(get_db)):

    async def _unblock_user():
        return await unblock_user(email, db)
    
    return await process_request(_unblock_user)


@router.get("/search/users")
async def search_all_users(search: str, db: AsyncSession = Depends(get_db)):

    async def _search_users():
        return await search_users(search, db)
    
    return await process_request(_search_users)