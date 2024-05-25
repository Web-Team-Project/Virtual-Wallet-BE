import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from fastapi import HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crud.auth_email import authenticate_user
from app.services.crud.wallet import add_funds_to_wallet, check_balance, create_wallet, withdraw_funds_from_wallet
from app.sql_app.models.enumerate import Currency
from app.sql_app.models.models import User, Wallet


@pytest.fixture
def db():
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock()))
    db.add = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def mock_user():
    mock_user = MagicMock(spec=User)
    mock_user.hashed_password = "hashed_password"
    mock_user.email_verified = True
    mock_user.id = uuid4()
    return mock_user


@pytest.mark.asyncio
async def test_create_wallet_success(db, mock_user):
    user_id = uuid4()
    currency = Currency.USD

    db.execute.return_value.scalar_one_or_none.return_value = mock_user

    with pytest.raises(HTTPException) as excinfo:
        await create_wallet(db, user_id, currency)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Wallet already exists for this user and currency."


@pytest.mark.asyncio
async def test_create_wallet_user_not_found(db):
    db.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await create_wallet(db, uuid4(), Currency.USD)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Wallet already exists for this user and currency."


@pytest.mark.asyncio
async def test_authenticate_user_with_valid_credentials(db, mock_user):
    mock_pwd_context = MagicMock()
    mock_pwd_context.verify = AsyncMock(return_value=True)

    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=mock_user)), \
         patch("app.services.crud.auth_email.pwd_context", new=mock_pwd_context):
        user = await authenticate_user(db, "user@example.com", "password")

    assert user == mock_user

@pytest.mark.asyncio
async def test_add_funds_to_wallet_existing_wallet(db, mock_user):
    mock_wallet = Wallet(user_id=mock_user.id, currency=Currency.USD, balance=100.0)
    db.execute.return_value.scalars().first.return_value = mock_wallet

    updated_wallet = await add_funds_to_wallet(db, amount=50.0, current_user=mock_user, currency=Currency.USD)

    assert updated_wallet.balance == 150.0
    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(mock_wallet)

@pytest.mark.asyncio
async def test_add_funds_to_wallet_non_existing_wallet(db, mock_user):
    db.execute.return_value.scalars().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await add_funds_to_wallet(db, amount=50.0, current_user=mock_user, currency=Currency.USD)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Wallet not found."
    db.execute.assert_called_once()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

@pytest.mark.asyncio
async def test_withdraw_funds_from_wallet_existing_wallet_sufficient_balance(db, mock_user):
    mock_wallet = Wallet(user_id=mock_user.id, currency=Currency.USD, balance=100.0)
    db.execute.return_value.scalars().first.return_value = mock_wallet

    updated_wallet = await withdraw_funds_from_wallet(db, current_user=mock_user, amount=50.0, currency=Currency.USD)

    assert updated_wallet.balance == 50.0
    db.execute.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(mock_wallet)

@pytest.mark.asyncio
async def test_withdraw_funds_from_wallet_existing_wallet_insufficient_balance(db, mock_user):
    mock_wallet = Wallet(user_id=mock_user.id, currency=Currency.USD, balance=30.0)
    db.execute.return_value.scalars().first.return_value = mock_wallet

    with pytest.raises(HTTPException) as exc_info:
        await withdraw_funds_from_wallet(db, current_user=mock_user, amount=50.0, currency=Currency.USD)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Insufficient funds."
    db.execute.assert_called_once()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

@pytest.mark.asyncio
async def test_withdraw_funds_from_wallet_non_existing_wallet(db, mock_user):
    db.execute.return_value.scalars().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await withdraw_funds_from_wallet(db, current_user=mock_user, amount=50.0, currency=Currency.USD)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Wallet not found."
    db.execute.assert_called_once()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

@pytest.mark.asyncio
async def test_check_balance_with_wallets(db, mock_user):
    mock_wallets = [
        Wallet(user_id=mock_user.id, currency=Currency.USD, balance=100.0),
        Wallet(user_id=mock_user.id, currency=Currency.EUR, balance=200.0),
    ]
    db.execute.return_value.scalars().all.return_value = mock_wallets

    balances = await check_balance(db, current_user=mock_user)

    assert len(balances) == 2
    assert (100.0, Currency.USD) in balances
    assert (200.0, Currency.EUR) in balances
    db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_check_balance_no_wallets(db, mock_user):
    db.execute.return_value.scalars().all.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await check_balance(db, current_user=mock_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "No wallets found."
    db.execute.assert_called_once()