import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from sqlalchemy import select
from app.sql_app.database import AsyncSessionLocal, Base, engine, get_db
from app.schemas.user import UserBase
from app.services.crud.user import create_user, user_info
from app.sql_app.models.models import Card, Category, Contact, Transaction, User
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def create_existing_user():
    existing_user_info = {
        "email": "existing@example.com",
        "sub": "existing_sub",
        # Other user info...
    }
    await create_user(existing_user_info)


@pytest.mark.asyncio
async def test_existing_user_update(create_existing_user):
    updated_user_info = {
        "email": "existing@example.com",
        "sub": "updated_sub",
        "name": "Updated Name",
        "given_name": "Updated",
        "family_name": "Name",
        "picture": "https://example.com/updated_picture.jpg",
        "email_verified": True,
        "locale": "en_US"
    }
    await create_user(updated_user_info)
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == "existing@example.com"))
        user = result.scalars().first()
        assert user.sub == "updated_sub", "User sub field was not updated correctly"
        assert user.name == "Updated Name", "User name was not updated correctly"
        assert user.given_name == "Updated", "User given_name was not updated correctly"
        assert user.family_name == "Name", "User family_name was not updated correctly"
        assert user.picture == "https://example.com/updated_picture.jpg", "User picture was not updated correctly"
        assert user.email_verified == True, "User email_verified was not updated correctly"
        assert user.locale == "en_US", "User locale was not updated correctly"


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    

@pytest.mark.asyncio
async def test_create_new_user():
    new_user_info = {
        "email": "new_user@example.com",
        "sub": "new_sub",
        "name": "New User",
        "given_name": "New",
        "family_name": "User",
        "picture": "https://example.com/new_user_picture.jpg",
        "email_verified": True,
        "locale": "en_US"
    }
    await create_user(new_user_info)
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == "new_user@example.com"))
        user = result.scalars().first()
        assert user is not None, "New user was not created"
        assert user.email == "new_user@example.com", "User email does not match"
        assert user.sub == "new_sub", "User sub does not match"
        assert user.name == "New User", "User name does not match"
        assert user.given_name == "New", "User given_name does not match"
        assert user.family_name == "User", "User family_name does not match"
        assert user.picture == "https://example.com/new_user_picture.jpg", "User picture does not match"
        assert user.email_verified == True, "User email_verified does not match"
        assert user.locale == "en_US", "User locale does not match"


@pytest.mark.asyncio
async def test_handle_commit_exception():
    userinfo = {...} 
    db = MagicMock(spec=AsyncSession)
    db.commit = AsyncMock(side_effect=Exception("Commit failed"))
    with patch("app.services.crud.user.AsyncSession", return_value=db):
        with pytest.raises(Exception):
            await create_user(userinfo)


@pytest.fixture
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def setup_test_data(async_session: AsyncSession):
    test_user = User(
        email="test@example.com",
        sub="test_sub",
        name="Test User",
        given_name="Test",
        family_name="User",
        email_verified=True,
        locale="en_US"
    )

    async with async_session.begin():
        async_session.add(test_user)
        await async_session.commit()
    yield test_user

@pytest.mark.asyncio
async def test_user_info(setup_test_data, async_session: AsyncSession):
    async for test_user in setup_test_data:
        assert test_user.email == "test@example.com"
        # Add more assertions as needed to test user information
