from datetime import datetime, timezone
import re
from uuid import UUID, uuid4
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import ANY, AsyncMock, MagicMock
import pytest

from app.schemas.transaction import TransactionCreate
from app.services.crud.transaction import approve_transaction, confirm_transaction, create_transaction, get_transactions_by_user_id
from app.sql_app.models.enumerate import Status
from app.sql_app.models.models import Card, Transaction, User, Wallet

def sql_string(query):
    """Convert SQLAlchemy query to its string representation."""
    return str(query.compile(compile_kwargs={"literal_binds": True}))

@pytest.mark.asyncio
async def test_create_transaction_success():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    recipient_id = uuid4()
    card_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.now(timezone.utc),
        card_id=card_id,
        recipient_id=recipient_id,
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=False)
    recipient_wallet = Wallet(user_id=recipient_id, balance=1000)
    sender_wallet = Wallet(user_id=sender_id, balance=200)
    card = Card(id=card_id, user_id=sender_id)

    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    sender_wallet_mock_result = MagicMock()
    sender_wallet_mock_result.scalars.return_value.first.return_value = sender_wallet

    card_mock_result = MagicMock()
    card_mock_result.scalars.return_value.first.return_value = card

    recipient_wallet_mock_result = MagicMock()
    recipient_wallet_mock_result.scalars.return_value.first.return_value = recipient_wallet

    db.execute = AsyncMock(side_effect=[
        sender_mock_result,
        sender_wallet_mock_result,
        card_mock_result,
        recipient_wallet_mock_result
    ])
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    transaction = await create_transaction(db, transaction_data, sender_id)

    expected_calls = [
        sql_string(select(User).where(User.id == sender_id)),
        sql_string(select(Wallet).where(Wallet.user_id == sender_id)),
        sql_string(select(Card).where(Card.id == card_id, Card.user_id == sender_id)),
        sql_string(select(Wallet).where(Wallet.user_id == recipient_id))
    ]

    actual_calls = [sql_string(call.args[0]) for call in db.execute.call_args_list]

    print("Expected calls:", expected_calls)
    print("Actual calls:", actual_calls)

    for expected_call in expected_calls:
        assert expected_call in actual_calls, f"Expected call not found: {expected_call}"

    db.add.assert_called_once_with(ANY)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ANY)

    assert transaction.amount == transaction_data.amount
    assert transaction.currency == transaction_data.currency
    assert transaction.card_id == transaction_data.card_id
    assert transaction.sender_id == sender_id
    assert transaction.recipient_id == transaction_data.recipient_id
    assert transaction.status == "pending"


@pytest.mark.asyncio
async def test_create_transaction_sender_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4()
    )

    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=sender_mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await create_transaction(db, transaction_data, sender_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Sender not found."


@pytest.mark.asyncio
async def test_create_transaction_sender_blocked():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=True)
    
    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    db.execute = AsyncMock(return_value=sender_mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await create_transaction(db, transaction_data, sender_id)

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Sender is blocked."


@pytest.mark.asyncio
async def test_create_transaction_sender_wallet_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=False)
    
    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    sender_wallet_mock_result = MagicMock()
    sender_wallet_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(side_effect=[
        sender_mock_result,
        sender_wallet_mock_result
    ])

    with pytest.raises(HTTPException) as excinfo:
        await create_transaction(db, transaction_data, sender_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Sender's wallet not found."


@pytest.mark.asyncio
async def test_create_transaction_insufficient_funds():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=50)
    
    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    sender_wallet_mock_result = MagicMock()
    sender_wallet_mock_result.scalars.return_value.first.return_value = sender_wallet

    db.execute = AsyncMock(side_effect=[
        sender_mock_result,
        sender_wallet_mock_result
    ])

    with pytest.raises(HTTPException) as excinfo:
        await create_transaction(db, transaction_data, sender_id)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Insufficient funds."


@pytest.mark.asyncio
async def test_create_transaction_card_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=uuid4(),
        recipient_id=uuid4(),
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=200)
    
    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    sender_wallet_mock_result = MagicMock()
    sender_wallet_mock_result.scalars.return_value.first.return_value = sender_wallet

    card_mock_result = MagicMock()
    card_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(side_effect=[
        sender_mock_result,
        sender_wallet_mock_result,
        card_mock_result
    ])

    with pytest.raises(HTTPException) as excinfo:
        await create_transaction(db, transaction_data, sender_id)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Card not found."


@pytest.mark.asyncio
async def test_create_transaction_recipient_wallet_not_found():
    db = AsyncMock(spec=AsyncSession)
    sender_id = uuid4()
    recipient_id = uuid4()
    card_id = uuid4()
    transaction_data = TransactionCreate(
        amount=100,
        currency="USD",
        timestamp=datetime.utcnow(),
        card_id=card_id,
        recipient_id=recipient_id,
        category_id=uuid4()
    )

    sender = User(id=sender_id, is_blocked=False)
    sender_wallet = Wallet(user_id=sender_id, balance=200)
    card = Card(id=card_id, user_id=sender_id)
    
    sender_mock_result = MagicMock()
    sender_mock_result.scalars.return_value.first.return_value = sender

    sender_wallet_mock_result = MagicMock()
    sender_wallet_mock_result.scalars.return_value.first.return_value = sender_wallet

    card_mock_result = MagicMock()
    card_mock_result.scalars.return_value.first.return_value = card

    recipient_wallet_mock_result = MagicMock()
    recipient_wallet_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(side_effect=[
        sender_mock_result,
        sender_wallet_mock_result,
        card_mock_result,
        recipient_wallet_mock_result
    ])
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await create_transaction(db, transaction_data, sender_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert re.match(r"\s*Recipient's wallet not found\s*", exc_info.value.detail)


    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_confirm_transaction_success():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = str(uuid.uuid4()) 
    current_user_id = str(uuid.uuid4()) 

    sender_id = current_user_id 

    transaction = Transaction(id=transaction_id, status=Status.pending, sender_id=sender_id)
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    transaction.status = Status.pending

    confirmed_transaction = await confirm_transaction(transaction_id, db, current_user_id)

    assert confirmed_transaction == transaction

@pytest.mark.asyncio
async def test_confirm_transaction_not_found():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = str(uuid4()) 
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await confirm_transaction(str(transaction_id), db, current_user_id)

    assert exc_info.value.status_code == 404
    assert "Transaction with id" in exc_info.value.detail
    assert "not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_confirm_transaction_already_confirmed():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    
    transaction = Transaction(id=transaction_id, status="confirmed", sender_id=sender_id)
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = transaction
    db.execute = AsyncMock(return_value=mock_result)

    current_user_id_str = str(current_user_id)

    with pytest.raises(HTTPException) as exc_info:
        await confirm_transaction(transaction_id, db, current_user_id_str)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You are not allowed to confirm this transaction."


@pytest.mark.asyncio
async def test_get_transactions_by_user_id_with_transactions():
    db = AsyncMock(spec=AsyncSession)
    user_id = uuid4()
    transactions = [
        Transaction(sender_id=user_id, amount=100, currency="USD"),
        Transaction(sender_id=user_id, amount=200, currency="EUR"),
        Transaction(sender_id=user_id, amount=300, currency="GBP")
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = transactions

    db.execute = AsyncMock(return_value=mock_result)

    result_transactions = await get_transactions_by_user_id(db, user_id)

    assert result_transactions == transactions


@pytest.mark.asyncio
async def test_get_transactions_by_user_id_no_transactions():
    db = AsyncMock(spec=AsyncSession)
    user_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    db.execute = AsyncMock(return_value=mock_result)

    result_transactions = await get_transactions_by_user_id(db, user_id)

    assert result_transactions == []


@pytest.mark.asyncio
async def test_get_transactions_by_user_id_with_transactions():
    db = AsyncMock(spec=AsyncSession)
    user_id = uuid4()
    transactions = [
        Transaction(sender_id=user_id, amount=100, currency="USD"),
        Transaction(sender_id=user_id, amount=200, currency="EUR"),
        Transaction(sender_id=user_id, amount=300, currency="GBP")
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = transactions

    db.execute = AsyncMock(return_value=mock_result)

    result_transactions = await get_transactions_by_user_id(db, user_id)

    assert result_transactions == transactions


def test_direct_comparison():
    transaction_recipient_id = UUID('bed1718a-fb0d-4c65-a29d-fd2ceef9b07d')
    current_user_id = UUID('bed1718a-fb0d-4c65-a29d-fd2ceef9b07d')
    assert transaction_recipient_id == current_user_id


@pytest.mark.asyncio
async def test_approve_transaction_success():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    recipient_id = current_user_id
    amount = 100

    transaction = Transaction(id=transaction_id, sender_id=sender_id, recipient_id=recipient_id, amount=amount, status=Status.awaiting)
    sender_wallet = Wallet(user_id=sender_id, balance=200)
    recipient_wallet = Wallet(user_id=recipient_id, balance=50)

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = transaction

    mock_sender_wallet_result = MagicMock()
    mock_sender_wallet_result.scalars.return_value.first.return_value = sender_wallet

    mock_recipient_wallet_result = MagicMock()
    mock_recipient_wallet_result.scalars.return_value.first.return_value = recipient_wallet

    db.execute = AsyncMock(side_effect=[
        mock_transaction_result,
        mock_sender_wallet_result,
        mock_recipient_wallet_result
    ])
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    approved_transaction = await approve_transaction(db, transaction_id, str(current_user_id))

    assert approved_transaction.status == Status.confirmed
    assert sender_wallet.balance == 100
    assert recipient_wallet.balance == 150
    db.commit.assert_called_once()
    db.refresh.assert_any_call(transaction)
    db.refresh.assert_any_call(sender_wallet)
    db.refresh.assert_any_call(recipient_wallet)


@pytest.mark.asyncio
async def test_approve_transaction_not_found():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=mock_transaction_result)

    with pytest.raises(HTTPException) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == f"Transaction with id {transaction_id} not found."


@pytest.mark.asyncio
async def test_approve_transaction_unauthorized_user():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    recipient_id = uuid4()  # Different from current_user_id
    amount = 100

    transaction = Transaction(id=transaction_id, sender_id=sender_id, recipient_id=recipient_id, amount=amount, status=Status.awaiting)

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_transaction_result)

    with pytest.raises(HTTPException) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "You are not allowed to approve this transaction."


@pytest.mark.asyncio
async def test_approve_transaction_invalid_status():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    recipient_id = current_user_id
    amount = 100

    transaction = Transaction(id=transaction_id, sender_id=sender_id, recipient_id=recipient_id, amount=amount, status=Status.pending)

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_transaction_result)

    with pytest.raises(HTTPException) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "You can only approve transactions that are awaiting your approval."


@pytest.mark.asyncio
async def test_approve_transaction_insufficient_funds():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    recipient_id = current_user_id
    amount = 200

    transaction = Transaction(id=transaction_id, sender_id=sender_id, recipient_id=recipient_id, amount=amount, status=Status.awaiting)
    sender_wallet = Wallet(user_id=sender_id, balance=100)
    recipient_wallet = Wallet(user_id=recipient_id, balance=50)

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = transaction

    mock_sender_wallet_result = MagicMock()
    mock_sender_wallet_result.scalars.return_value.first.return_value = sender_wallet

    mock_recipient_wallet_result = MagicMock()
    mock_recipient_wallet_result.scalars.return_value.first.return_value = recipient_wallet

    db.execute = AsyncMock(side_effect=[
        mock_transaction_result,
        mock_sender_wallet_result,
        mock_recipient_wallet_result
    ])

    with pytest.raises(HTTPException) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Insufficient funds."


@pytest.mark.asyncio
async def test_approve_transaction_database_error():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()

    db.execute = AsyncMock(side_effect=Exception("Database error"))

    with pytest.raises(Exception) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert str(excinfo.value) == "Database error"


@pytest.mark.asyncio
async def test_approve_transaction_already_confirmed():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    sender_id = uuid4()
    recipient_id = current_user_id
    amount = 100

    transaction = Transaction(id=transaction_id, sender_id=sender_id, recipient_id=recipient_id, amount=amount, status=Status.confirmed)

    mock_transaction_result = MagicMock()
    mock_transaction_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_transaction_result)

    with pytest.raises(HTTPException) as excinfo:
        await approve_transaction(db, transaction_id, str(current_user_id))

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "You can only approve transactions that are awaiting your approval."


# @pytest.mark.asyncio
# async def test_reject_transaction_success():
#     async with AsyncSession() as db:
#         transaction_id = uuid4()
#         current_user_id = str(uuid4())

#         transaction = Transaction(id=transaction_id, sender_id=uuid4(), recipient_id=uuid4(), status=Status.awaiting)

#         mock_result = MagicMock()
#         mock_result.scalars.return_value.first.return_value = transaction

#         db.execute = MagicMock(return_value=mock_result)

#         try:
#             current_user_id = UUID(current_user_id)
#             await reject_transaction(db, transaction_id, current_user_id)
#         except Exception as e:
#             assert False, f"Exception occurred: {e}"



# @pytest.mark.asyncio
# async def test_reject_transaction_not_found():
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = uuid4()
#     current_user_id = uuid4()

#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = None

#     db.execute = AsyncMock(return_value=mock_result)

#     with pytest.raises(HTTPException) as excinfo:
#         await reject_transaction(db, transaction_id, str(current_user_id))

#     assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
#     assert excinfo.value.detail == f"Transaction with id {transaction_id} not found."


# @pytest.mark.asyncio
# async def test_reject_transaction_unauthorized_user():
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = uuid4()
#     current_user_id = uuid4()
#     recipient_id = uuid4()  # Different from current_user_id

#     transaction = Transaction(id=transaction_id, recipient_id=recipient_id, status=Status.awaiting)

#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = transaction

#     db.execute = AsyncMock(return_value=mock_result)

#     with pytest.raises(HTTPException) as excinfo:
#         await reject_transaction(db, transaction_id, str(current_user_id))

#     assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
#     assert excinfo.value.detail == "You are not allowed to reject this transaction."


# @pytest.mark.asyncio
# async def test_reject_transaction_invalid_status():
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = uuid4()
#     current_user_id = uuid4()
#     recipient_id = current_user_id

#     transaction = Transaction(id=transaction_id, recipient_id=recipient_id, status=Status.pending)

#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = transaction

#     db.execute = AsyncMock(return_value=mock_result)

#     with pytest.raises(HTTPException) as excinfo:
#         await reject_transaction(db, transaction_id, str(current_user_id))

#     assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert excinfo.value.detail == "You can only reject awaiting transactions."


# @pytest.mark.asyncio
# async def test_reject_transaction_database_error():
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = uuid4()
#     current_user_id = uuid4()

#     db.execute = AsyncMock(side_effect=Exception("Database error"))

#     with pytest.raises(Exception) as excinfo:
#         await reject_transaction(db, transaction_id, str(current_user_id))

#     assert str(excinfo.value) == "Database error"


# @pytest.mark.asyncio
# async def test_reject_transaction_already_declined():
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = uuid4()
#     current_user_id = uuid4()
#     recipient_id = current_user_id

#     transaction = Transaction(id=transaction_id, recipient_id=recipient_id, status=Status.declined)

#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = transaction

#     db.execute = AsyncMock(return_value=mock_result)

#     with pytest.raises(HTTPException) as excinfo:
#         await reject_transaction(db, transaction_id, str(current_user_id))

#     assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert excinfo.value.detail == "You can only reject awaiting transactions."
