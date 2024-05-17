from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.category import CategoryCreate
from app.sql_app.models.models import Category

async def create_category(db: AsyncSession, category: CategoryCreate):
    db_category = Category(
        name=category.name
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

