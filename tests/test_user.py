from datetime import datetime, timezone
import re
from uuid import UUID, uuid4
from fastapi import HTTPException, status
from requests import patch
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import ANY, AsyncMock, MagicMock
import pytest

from app.schemas.user import UserBase
from app.services.crud.user import create_user, user_info
from app.sql_app.models.models import Card, Category, Contact, Transaction, User


@pytest.mark.asyncio
async def test_create_new_user():
    db = AsyncMock(spec=AsyncSession)
    userinfo = {
        "sub": "1234567890",
        "name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "http://example.com/johndoe.jpg",
        "email": "john.doe@example.com",
        "email_verified": True,
        "locale": "en"
    }

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    await create_user(userinfo, db)

    expected_query = str(select(User).where(User.email == userinfo["email"]))
    actual_query = str(db.execute.call_args[0][0])
    
    assert expected_query == actual_query, f"Expected: {expected_query}, but got: {actual_query}"
    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_existing_user():
    db = AsyncMock(spec=AsyncSession)
    userinfo = {
        "sub": "1234567890",
        "name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "http://example.com/johndoe.jpg",
        "email": "john.doe@example.com",
        "email_verified": True,
        "locale": "en"
    }

    existing_user = User(
        sub="old_sub",
        name="Old Name",
        given_name="Old Given Name",
        family_name="Old Family Name",
        picture="http://example.com/oldpicture.jpg",
        email="john.doe@example.com",
        email_verified=False,
        locale="old_locale",
        is_admin=False,
        is_active=False,
        is_blocked=True,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_user
    db.execute = AsyncMock(return_value=mock_result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    await create_user(userinfo, db)

    expected_select_query = str(select(User).where(User.email == userinfo["email"]))
    actual_select_query = str(db.execute.call_args_list[0][0][0])
    assert expected_select_query == actual_select_query, f"Expected: {expected_select_query}, but got: {actual_select_query}"

    expected_update_query = (
        update(User)
        .where(User.email == userinfo["email"])
        .values(
            sub=userinfo["sub"],
            name=userinfo["name"],
            given_name=userinfo["given_name"],
            family_name=userinfo["family_name"],
            picture=userinfo["picture"],
            email_verified=userinfo["email_verified"],
            locale=userinfo["locale"],
            is_active=True,
            is_blocked=False,
            is_admin=existing_user.is_admin,
        )
    )
    actual_update_query = db.execute.call_args_list[1][0][0]
    assert str(expected_update_query) == str(actual_update_query), f"Expected: {expected_update_query}, but got: {actual_update_query}"

##########

# @pytest.fixture
# def mock_db():
#     return AsyncMock(spec=AsyncSession)

# @pytest.fixture
# def mock_user():
#     return UserBase(
#         id=uuid4(),
#         sub="1234567890",
#         name="John Doe",
#         given_name="John",
#         family_name="Doe",
#         picture="http://example.com/johndoe.jpg",
#         email="john.doe@example.com",
#         email_verified=True,
#         locale="en"
#     )

# @pytest.fixture
# def mock_data():
#     cards = [Card(id=1, user_id=1, name="Card 1")]  # Update card_name to name
#     categories = [Category(id=1, user_id=1, category_name="Category 1")]
#     contacts = [Contact(id=1, user_id=1, contact_name="Contact 1")]
#     transactions = [Transaction(id=1, card_id=1, amount=100.0)]
#     return cards, categories, contacts, transactions

# @pytest.mark.asyncio
# async def test_fetch_cards(mock_db, mock_user, mock_data):
#     cards, _, _, _ = mock_data
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = cards
#     mock_db.execute = AsyncMock(return_value=mock_result)

#     result = await mock_db.execute(select(Card).where(Card.user_id == mock_user.id))
#     assert result.scalars().all() == cards

# @pytest.mark.asyncio
# async def test_user_base_initialization(mock_user):
#     assert mock_user.id is not None
#     assert mock_user.email == "john.doe@example.com"


# @pytest.mark.asyncio
# async def test_fetch_categories(mock_db, mock_user, mock_data):
#     _, categories, _, _ = mock_data
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = categories
#     mock_db.execute = AsyncMock(return_value=mock_result)

#     result = await mock_db.execute(select(Category).where(Category.user_id == mock_user.id))
#     assert result.scalars().all() == categories

# @pytest.mark.asyncio
# async def test_fetch_contacts(mock_db, mock_user, mock_data):
#     _, _, contacts, _ = mock_data
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = contacts
#     mock_db.execute = AsyncMock(return_value=mock_result)

#     result = await mock_db.execute(select(Contact).where(Contact.user_id == mock_user.id))
#     assert result.scalars().all() == contacts

# @pytest.mark.asyncio
# async def test_fetch_transactions(mock_db, mock_user, mock_data):
#     _, _, _, transactions = mock_data
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = transactions
#     mock_db.execute = AsyncMock(return_value=mock_result)

#     result = await mock_db.execute(select(Transaction).join(Card).where(Card.user_id == mock_user.id))
#     assert result.scalars().all() == transactions

# @pytest.mark.asyncio
# async def test_user_info(mock_db, mock_user, mock_data):
#     cards, categories, contacts, transactions = mock_data

#     mock_cards_result = MagicMock()
#     mock_cards_result.scalars.return_value.all.return_value = cards
#     mock_db.execute = AsyncMock(side_effect=[mock_cards_result])

#     mock_categories_result = MagicMock()
#     mock_categories_result.scalars.return_value.all.return_value = categories
#     mock_db.execute.side_effect = [mock_cards_result, mock_categories_result]

#     mock_contacts_result = MagicMock()
#     mock_contacts_result.scalars.return_value.all.return_value = contacts
#     mock_db.execute.side_effect = [mock_cards_result, mock_categories_result, mock_contacts_result]

#     mock_transactions_result = MagicMock()
#     mock_transactions_result.scalars.return_value.all.return_value = transactions
#     mock_db.execute.side_effect = [mock_cards_result, mock_categories_result, mock_contacts_result, mock_transactions_result]

#     result = await user_info(mock_db, mock_user)

#     assert result["email"] == mock_user.email
#     assert result["cards"] == cards
#     assert result["categories"] == categories
#     assert result["contacts"] == contacts
#     assert result["transactions"] == transactions

#     # Verify that the db.execute method was called with the expected queries
#     assert str(mock_db.execute.call_args_list[0][0][0]) == str(select(Card).where(Card.user_id == mock_user.id))
#     assert str(mock_db.execute.call_args_list[1][0][0]) == str(select(Category).where(Category.user_id == mock_user.id))
#     assert str(mock_db.execute.call_args_list[2][0][0]) == str(select(Contact).where(Contact.user_id == mock_user.id))
#     assert str(mock_db.execute.call_args_list[3][0][0]) == str(select(Transaction).join(Card).where(Card.user_id == mock_user.id))
