from datetime import datetime, timedelta
from pydantic import ValidationError
import pytest
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, patch
from uuid import uuid4
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.transaction import RecurringTransactionCreate, TransactionCreate
from app.services.crud.recurring_transaction import create_recurring_transaction, process_recurring_transactions
from app.sql_app.models.models import Card, User, Wallet

@pytest.mark.asyncio
async def test_create_recurring_transaction_success():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    recipient_id = uuid4()
    card_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=card_id,
        recipient_id=recipient_id,
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily' instead of 'days'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=200.0)
    card = Card(id=card_id, user_id=sender_id)
    recipient_wallet = Wallet(user_id=recipient_id)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender_wallet)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=card)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=recipient_wallet))))
    ])
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    new_transaction = await create_recurring_transaction(db, transaction_data, sender_id)

    assert new_transaction.user_id == sender_id
    assert new_transaction.card_id == card_id
    assert new_transaction.recipient_id == recipient_id
    assert new_transaction.amount == transaction_data.amount
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(new_transaction)


@pytest.mark.asyncio
async def test_create_recurring_transaction_sender_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Sender not found."


@pytest.mark.asyncio
async def test_create_recurring_transaction_sender_blocked():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=True)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender))))
    ])

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Sender is blocked."


@pytest.mark.asyncio
async def test_create_recurring_transaction_sender_wallet_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=False)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
    ])

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Sender's wallet not found."


@pytest.mark.asyncio
async def test_create_recurring_transaction_insufficient_funds():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=50.0)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender_wallet))))
    ])

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Insufficient funds."


@pytest.mark.asyncio
async def test_create_recurring_transaction_card_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=200.0)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender_wallet)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
    ])

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Card not found."


@pytest.mark.asyncio
async def test_create_recurring_transaction_recipient_wallet_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = RecurringTransactionCreate(
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4(),
        amount=100.0,
        interval=30,
        interval_type="daily",  # Updated to use 'daily'
        next_execution_date="2024-06-01"
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=200.0)
    card = Card(id=transaction_data.card_id, user_id=sender_id)

    db.execute = AsyncMock(side_effect=[
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sender_wallet)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=card)))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
    ])

    with pytest.raises(HTTPException) as exc_info:
        await create_recurring_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Recipient's wallet not found."


@pytest.mark.asyncio
async def test_create_recurring_transaction_invalid_interval_type():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()

    with pytest.raises(ValidationError) as exc_info:
        transaction_data = RecurringTransactionCreate(
            card_id=uuid4(),
            recipient_id=uuid4(),
            category_id=uuid4(),
            amount=100.0,
            interval=30,
            interval_type="invalid",  # Invalid interval type
            next_execution_date="2024-06-01"
        )
    
    assert "Input should be 'daily', 'weekly' or 'monthly'" in str(exc_info.value)


@pytest.mark.asyncio
async def test_no_due_transactions():
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=[])))
    
    await process_recurring_transactions(db)
    
    db.commit.assert_not_called()
