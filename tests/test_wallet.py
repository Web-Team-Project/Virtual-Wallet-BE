from unittest.mock import Mock, patch
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.sql_app.database import get_db

from app.services.crud.wallet import create_wallet
from app.sql_app.models.enumerate import Currency
from app.sql_app.models.models import Wallet

# @pytest.mark.asyncio
# async def test_create_wallet_new_wallet():
#     # Mocking get_db() function directly
#     async def mock_get_db():
#         return Mock()

#     # Replace the original get_db() with the mock function
#     create_wallet.get_db = mock_get_db

#     # Your test code
#     user_id = uuid.uuid4()
#     currency = Currency.USD

#     # Provide both arguments
#     created_wallet = await create_wallet(user_id=user_id, currency=currency)

#     assert isinstance(created_wallet, Wallet)
#     assert created_wallet.user_id == user_id
#     assert created_wallet.currency == currency
#     assert created_wallet.balance == 0.0


# @pytest.mark.asyncio
# async def test_create_wallet_existing_wallet():
#     # Mocking get_db() function directly
#     async def mock_get_db():
#         return Mock()

#     # Replace the original get_db() with the mock function
#     create_wallet.get_db = mock_get_db

#     # Your test code
#     user_id = uuid.uuid4()
#     currency = Currency.BGN

#     # Use the correct path to get_db() function
#     with patch('app.sql_app.database.get_db') as mock_get_db:
#         mock_get_db.return_value = Mock()
#         created_wallet = await create_wallet(user_id=user_id, currency=currency)

#     assert isinstance(created_wallet, Wallet)
#     assert created_wallet.user_id == user_id
#     assert created_wallet.currency == currency
#     assert created_wallet.balance == 0.0