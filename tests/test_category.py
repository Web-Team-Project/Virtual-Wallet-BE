from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import ANY, AsyncMock, MagicMock
import pytest
from sqlalchemy.orm import selectinload

from app.schemas.category import CategoryCreate
from app.services.crud.category import create_category, delete_category, read_categories
from app.sql_app.models.models import Category, Transaction



@pytest.mark.asyncio
async def test_create_category_success():
    db = MagicMock(spec=AsyncSession)
    user_id = str(uuid4())
    category_data = Category(name="Test Category")
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await create_category(db, category_data, user_id)

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)
    assert result.name == "Test Category"
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_create_category_already_exists():
    db = MagicMock(spec=AsyncSession)
    user_id = str(uuid4())
    category_data = CategoryCreate(name="Test Category")
    mock_category = Category(id=uuid4(), name="Test Category", user_id=user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_category
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await create_category(db, category_data, user_id)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Category already exists."


@pytest.mark.asyncio
async def test_read_categories():
    db = MagicMock(spec=AsyncSession)
    user_id = str(uuid4())
    
    mock_categories = [
        Category(id=uuid4(), name="Category 1", user_id=user_id, transactions=[Transaction(), Transaction()]),
        Category(id=uuid4(), name="Category 2", user_id=user_id, transactions=[Transaction(), Transaction()]),
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_categories
    db.execute = AsyncMock(return_value=mock_result)

    result = await read_categories(db, user_id)

    db.execute.assert_awaited_once_with(ANY)
    assert "categories" in result
    assert len(result["categories"]) == len(mock_categories)
    for category in result["categories"]:
        assert isinstance(category, Category)
        assert category.user_id == user_id
        assert hasattr(category, "transactions")
        assert isinstance(category.transactions, list)
        assert len(category.transactions) == 2


@pytest.mark.asyncio
async def test_delete_category_success():
    db = AsyncMock(spec=AsyncSession)

    category_name = "Test Category"
    user_id = "test_user_id"

    mock_category = Category(name=category_name, user_id=user_id)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_category
    db.execute = AsyncMock(return_value=mock_result)

    response = await delete_category(db, category_name, user_id)

    expected_query = select(Category).where(and_(Category.name == category_name, Category.user_id == user_id))
    db.execute.assert_awaited_once()
    assert str(db.execute.await_args[0][0]) == str(expected_query)
    db.delete.assert_awaited_once_with(mock_category)
    db.commit.assert_awaited_once()
    assert response == {"message": "Category has been deleted."}

@pytest.mark.asyncio
async def test_delete_category_not_found():
    db = AsyncMock(spec=AsyncSession)

    category_name = "Test Category"
    user_id = "test_user_id"

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await delete_category(db, category_name, user_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Category not found."

    expected_query = select(Category).where(and_(Category.name == category_name, Category.user_id == user_id))
    db.execute.assert_awaited_once()
    assert str(db.execute.await_args[0][0]) == str(expected_query)
    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()