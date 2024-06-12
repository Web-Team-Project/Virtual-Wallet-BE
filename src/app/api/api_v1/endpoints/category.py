from fastapi import APIRouter, Depends
from app.schemas.category import CategoryCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.common.utils import get_current_user, process_request
from app.sql_app.database import get_db
from app.services.crud.category import create_category, delete_category, read_categories
from app.sql_app.models.models import User, Category
import logging

router = APIRouter()


@router.post("/categories")
async def create(category: CategoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new category for the user. 
    The category will be used to classify transactions.
        Parameters:
            category (CategoryCreate): The category data.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Category: The created category object.
    """
    logging.info("Creating new category")
    async def _create_category() -> Category:
        return await create_category(db, category, current_user.id)
    logging.info("Category created")
    return await process_request(_create_category)


@router.get("/categories")
async def view_categories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    View the categories created by the user.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            List[Category]: The list of categories.
    """
    logging.info("Getting categories")
    async def _read_categories() -> list[Category]:
        return await read_categories(db, current_user.id)
    logging.info("Categories retrieved")
    return await process_request(_read_categories)


@router.delete("/categories")
async def delete(category_name: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a category for the user. 
    The category will be removed from the user's list of categories.
        Parameters:
            category_name (str): The name of the category to delete.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            Category: The deleted category object.
    """
    logging.info("Deleting category")
    async def _delete_category() -> Category:
        return await delete_category(db, category_name, current_user.id)
    logging.info("Category deleted")
    return await process_request(_delete_category)