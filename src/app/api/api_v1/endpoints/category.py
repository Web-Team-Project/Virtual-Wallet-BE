from fastapi import APIRouter, Depends
from app.schemas.category import CategoryCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.common.utils import process_request
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.services.crud.category import create_category 
from app.sql_app.models.models import User, Category

router = APIRouter()

@router.post("/categories")
async def create(category: CategoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    async def _create_category() -> Category:
        return await create_category(db, category)

    return await process_request(_create_category)

