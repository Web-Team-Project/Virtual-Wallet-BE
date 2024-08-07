from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.schemas.card import CardCreate
from app.schemas.user import User
from app.services.crud.card import (
    create_card,
    delete_card,
    read_all_cards,
    read_card,
    update_card,
)
from app.sql_app.models.models import Card
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_card_success():
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    card_data = CardCreate(
        number="1234567890123456",
        card_holder="Test User",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )
    user_id = uuid4()

    result = await create_card(db, card_data, user_id)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_create_card_returns_error():
    db = MagicMock(spec=AsyncSession)
    existing_card = MagicMock()
    db.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_card))
    )

    card_data = CardCreate(
        number="1234567890123456",
        card_holder="Test User",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )
    user_id = uuid4()

    with pytest.raises(HTTPException) as excinfo:
        await create_card(db, card_data, user_id)

    assert excinfo.value.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert excinfo.value.detail == f"Card with id {card_data.number} is taken."


@pytest.mark.asyncio
async def test_read_card_success():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()
    mock_card = Card(
        id=card_id,
        user_id=user_id,
        number="1234567890123456",
        card_holder="Test User",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_card
    db.execute = AsyncMock(return_value=mock_result)

    result = await read_card(db, card_id, user_id)

    assert result == mock_card


@pytest.mark.asyncio
async def test_read_card_not_found():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await read_card(db, card_id, user_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert (
        excinfo.value.detail == f"Card with id {card_id} not found for user {user_id}."
    )


@pytest.mark.asyncio
async def test_read_all_cards_success():
    db = MagicMock(spec=AsyncSession)
    user_id = uuid4()
    card1 = Card(
        id=uuid4(),
        user_id=user_id,
        number="1234567890123456",
        card_holder="Test User 1",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )
    card2 = Card(
        id=uuid4(),
        user_id=user_id,
        number="6543210987654321",
        card_holder="Test User 2",
        exp_date="01/25",
        cvv="321",
        design="Design2",
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [card1, card2]
    db.execute = AsyncMock(return_value=mock_result)

    result = await read_all_cards(db, user_id)

    assert len(result) == 2
    assert result[0] == card1
    assert result[1] == card2


@pytest.mark.asyncio
async def test_update_card_success():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()
    mock_card = Card(
        id=card_id,
        user_id=user_id,
        number="1234567890123456",
        card_holder="Test User",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )
    updated_card_data = CardCreate(
        number="6543210987654321",
        card_holder="Updated User",
        exp_date="01/24",
        cvv="321",
        design="Design2",
    )

    current_user = User(
        id=user_id,
        sub="user_sub",
        name="Test User",
        given_name="Test",
        family_name="User",
        picture="http://example.com/picture.jpg",
        email="testuser@example.com",
        email_verified=True,
        locale="en",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_card
    db.execute = AsyncMock(return_value=mock_result)

    result = await update_card(db, card_id, updated_card_data, current_user)

    assert result.number == updated_card_data.number
    assert result.card_holder == updated_card_data.card_holder
    assert result.exp_date == updated_card_data.exp_date
    assert result.cvv == updated_card_data.cvv
    assert result.design == updated_card_data.design


@pytest.mark.asyncio
async def test_update_card_not_found():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()
    updated_card_data = CardCreate(
        number="6543210987654321",
        card_holder="Updated User",
        exp_date="01/24",
        cvv="321",
        design="Design2",
    )

    current_user = User(
        id=user_id,
        sub="user_sub",
        name="Test User",
        given_name="Test",
        family_name="User",
        picture="http://example.com/picture.jpg",
        email="testuser@example.com",
        email_verified=True,
        locale="en",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await update_card(db, card_id, updated_card_data, current_user)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Card not found."


@pytest.mark.asyncio
async def test_update_card_unauthorized():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    card_owner_id = uuid4()
    current_user_id = uuid4()
    mock_card = Card(
        id=card_id,
        user_id=card_owner_id,
        number="1234567890123456",
        card_holder="Test User",
        exp_date=date(2024, 11, 1),
        cvv="123",
        design="Design1",
    )
    updated_card_data = CardCreate(
        number="6543210987654321",
        card_holder="Updated User",
        exp_date="01/24",
        cvv="321",
        design="Design2",
    )


@pytest.mark.asyncio
async def test_delete_card_success():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()
    mock_card = Card(
        id=card_id,
        user_id=user_id,
        number="1234567890123456",
        card_holder="Test User",
        exp_date="01/24",
        cvv="123",
        design="Design1",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_card
    db.execute = AsyncMock(return_value=mock_result)

    db.delete = AsyncMock()
    db.commit = AsyncMock()

    result = await delete_card(db, card_id, user_id)

    db.delete.assert_awaited_once_with(mock_card)
    db.commit.assert_awaited_once()
    assert result == {"message": "Card deleted successfully."}


@pytest.mark.asyncio
async def test_delete_card_not_found():
    db = MagicMock(spec=AsyncSession)
    card_id = uuid4()
    user_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await delete_card(db, card_id, user_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Card not found."
