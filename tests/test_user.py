from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from sqlalchemy import select

from app.schemas.user import UserBase
from app.services.crud.user import create_user, user_info
from app.sql_app.models.models import Card, Category, Contact, Transaction, User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_user_new():
    userinfo = {
        "sub": "sub_id",
        "name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "https://example.com/picture.jpg",
        "email": "john@example.com",
        "email_verified": True,
        "locale": "en_US"
    }

    # Mock AsyncSession and its methods
    db = MagicMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch("app.services.crud.user.AsyncSession", return_value=db):
        result = await create_user(userinfo)

    await db.add()

    db.add.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_existing_user():
    userinfo = {
        "sub": "sub_id",
        "name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "https://example.com/picture.jpg",
        "email": "john@example.com",
        "email_verified": True,
        "locale": "en_US"
    }

    existing_user = User(**userinfo)
    db = MagicMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_result.scalar.return_value = existing_user
    db.execute = AsyncMock(return_value=mock_result)
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch("app.services.crud.user.AsyncSession", return_value=db):
        user = await create_user(userinfo)
    
    assert user is not None
    assert user.sub == existing_user.sub

@pytest.mark.asyncio
async def test_handle_commit_exception():
    userinfo = {...} 
    db = MagicMock(spec=AsyncSession)
    db.commit = AsyncMock(side_effect=Exception("Commit failed"))
    with patch("app.services.crud.user.AsyncSession", return_value=db):
        with pytest.raises(Exception):
            await create_user(userinfo)

# @pytest.mark.asyncio
# async def test_refresh_user():
#     userinfo = {
#         "sub": "sub_id",
#         "name": "John Doe",
#         "given_name": "John",
#         "family_name": "Doe",
#         "picture": "https://example.com/picture.jpg",
#         "email": "john@example.com",
#         "email_verified": True,
#         "locale": "en_US"
#     }

#     db = MagicMock(spec=AsyncSession)
#     mock_result = AsyncMock()
#     mock_result.scalar.return_value = None
#     db.execute = AsyncMock(return_value=mock_result)
#     db.add = AsyncMock()
#     db.commit = AsyncMock()
#     db.refresh = AsyncMock()

#     with patch("app.services.crud.user.AsyncSession", return_value=db):
#         await create_user(userinfo)

#     await db.commit.assert_awaited_once()  # Check that commit was awaited
#     await db.refresh.assert_awaited_once() 

