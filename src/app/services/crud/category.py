from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.category import CategoryCreate
from app.sql_app.models.models import Category


async def create_category(db: AsyncSession, category: CategoryCreate, user_id: str):
    """
    Create a new category for the user. It checks if category with the same name already exists.
        Parameters:
            db (AsyncSession): The database session.
            category (CategoryCreate): The category data.
            user_id (str): The ID of the user.
        Returns:
            Category: The created category object.
    """
    existing_category = await db.execute(select(Category).where(and_(Category.name == category.name, Category.user_id == user_id)))
    existing_category = existing_category.scalars().first()
    if existing_category is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Category already exists.")
    db_category = Category(name=category.name, user_id=user_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def read_categories(db: AsyncSession, user_id: str):
    """
    View all categories for the user and transactions associated with them.
        Parameters:
            db (AsyncSession): The database session.
            user_id (str): The ID of the user.
        Returns:
            dict: A dictionary with the categories and their transactions.
    """
    result = await db.execute(select(Category).options(selectinload(Category.transactions)).where(Category.user_id == user_id))
    categories = result.scalars().all()
    return {"categories": categories}


async def delete_category(db: AsyncSession, category_name: str, user_id: str):
    """
    Delete category by name.
        Parameters:
            db (AsyncSession): The database session.
            category_name (str): The name of the category.
            user_id (str): The ID of the user.
        Returns:
            dict: A message confirming the deletion.
    """
    db_category = await db.execute(select(Category).where(and_(Category.name == category_name, Category.user_id == user_id)))
    db_category = db_category.scalars().first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Category not found.")
    await db.delete(db_category)
    await db.commit()
    return {"message": "Category has been deleted."}