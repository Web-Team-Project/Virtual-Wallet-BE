from datetime import date
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock
import pytest
from app.schemas.card import CardCreate
from app.services.crud.card import create_card


@pytest.mark.asyncio
async def test_create_card():
    db = MagicMock(spec=AsyncSession)
    card_data = CardCreate(number="1234567890123456", 
                           card_holder="Test User", 
                           exp_date=date(2024, 11, 1), 
                           cvv="123", 
                           design="Design1")
    user_id = uuid4()
 
    result = await create_card(db, card_data, user_id)
 
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result.user_id == user_id