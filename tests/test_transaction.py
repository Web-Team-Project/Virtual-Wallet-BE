from datetime import datetime, timezone
import re
from uuid import UUID, uuid4
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import ANY, AsyncMock, MagicMock
import pytest

from app.schemas.transaction import TransactionCreate, TransactionFilter
from app.services.crud.transaction import approve_transaction, confirm_transaction, create_transaction, deny_transaction, get_transactions, get_transactions_by_user_id, reject_transaction
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
    transaction_id = uuid4()
    current_user_id = uuid4()
    transaction = Transaction(id=transaction_id, status="pending")
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    confirmed_transaction = await confirm_transaction(transaction_id, db, current_user)

    assert confirmed_transaction.status == "awaiting"
    assert db.commit.called
    assert db.refresh.called


@pytest.mark.asyncio
async def test_confirm_transaction_not_found():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await confirm_transaction(transaction_id, db, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Transaction not found."


@pytest.mark.asyncio
async def test_confirm_transaction_already_confirmed():
    db = AsyncMock(spec=AsyncSession)
    transaction_id = uuid4()
    current_user_id = uuid4()
    transaction = Transaction(id=transaction_id, status="confirmed")
    current_user = User(id=current_user_id)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = transaction

    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await confirm_transaction(transaction_id, db, current_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Transaction is already confirmed."


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


# @pytest.mark.asyncio
# async def test_get_transactions_as_admin():
#     db = AsyncMock(spec=AsyncSession)

#     admin_user = User(id=uuid4(), is_admin=True)

#     filter_params = TransactionFilter(start_date=datetime(2024, 1, 1), end_date=datetime(2024, 12, 31))
    
#     transactions = [
#         Transaction(amount=100, currency="USD", timestamp=datetime.utcnow()),
#         Transaction(amount=200, currency="EUR", timestamp=datetime.utcnow()),
#         Transaction(amount=300, currency="GBP", timestamp=datetime.utcnow())
#     ]

#     mock_result_count = MagicMock()
#     mock_result_count.scalar.return_value = 3

#     mock_result_transactions = MagicMock()
#     mock_result_transactions.scalars.return_value.all.return_value = transactions

#     db.execute = AsyncMock(side_effect=[mock_result_count, mock_result_transactions])

#     result = await get_transactions(db, admin_user, filter_params, skip=0, limit=10)

#     assert result.total == 3
#     assert len(result.transactions) == 3
#     assert isinstance(result.transactions[0], Transaction)


# @pytest.mark.asyncio
# async def test_approve_transaction_valid():
#     # Mock the database session
#     db = AsyncMock(spec=AsyncSession)

#     # Create a valid transaction ID and current user ID
#     transaction_id = uuid4()
#     current_user_id = uuid4()

#     # Create a transaction with status "awaiting" and correct recipient ID
#     transaction = TransactionCreate(id=transaction_id, status=Status.awaiting, sender_id=uuid4(), recipient_id=current_user_id, amount=100)

#     # Mock the database session to return the transaction wrapped in a Result object
#     result = AsyncMock()
#     result.scalar.return_value = transaction
#     db.execute = AsyncMock(return_value=result)

#     # Call the function being tested
#     result = await approve_transaction(db, transaction_id, current_user_id)

#     # Assert that the transaction status is updated to "confirmed"
#     assert result.status == Status.confirmed

# @pytest.mark.asyncio
# async def test_approve_transaction_valid():
#     # Mock the database session and query result
#     db = AsyncMock(spec=AsyncSession)
#     result = AsyncMock()
#     result.scalar.return_value = Transaction(
#         id=UUID("00000000-0000-0000-0000-000000000001"),  # Example transaction ID
#         recipient_id=UUID("00000000-0000-0000-0000-000000000002"),  # Example recipient ID
#         status=Status.awaiting,
#         sender_id=UUID("00000000-0000-0000-0000-000000000003"),  # Example sender ID
#         amount=100
#     )
#     db.execute.return_value = result

#     # Call the function being tested
#     transaction = await approve_transaction(db, UUID("00000000-0000-0000-0000-000000000001"), UUID("00000000-0000-0000-0000-000000000002"))

#     # Assert the transaction object returned by the function
#     assert isinstance(transaction, Transaction)
#     assert transaction.id == UUID("00000000-0000-0000-0000-000000000001")
#     assert transaction.recipient_id == UUID("00000000-0000-0000-0000-000000000002")
#     assert transaction.status == Status.confirmed

# @pytest.mark.asyncio
# async def test_approve_transaction_transaction_not_found():
#     # Mock the database session to return None for the transaction
#     db = AsyncMock(spec=AsyncSession)
#     result = AsyncMock()
#     result.scalar.return_value = None
#     db.execute.return_value = result

#     # Call the function being tested
#     with pytest.raises(HTTPException) as exc_info:
#         await approve_transaction(db, UUID("00000000-0000-0000-0000-000000000001"), UUID("00000000-0000-0000-0000-000000000002"))

#     # Assert the HTTPException is raised with the correct status code and detail message
#     assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
#     assert "Transaction with id" in exc_info.value.detail


# @pytest.mark.asyncio
# async def test_reject_transaction_success():
#     # Mock the database session and query result
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = UUID("00000000-0000-0000-0000-000000000001")
#     current_user_id = UUID("00000000-0000-0000-0000-000000000002")
#     mock_transaction = Transaction(id=transaction_id, recipient_id=current_user_id, status=Status.pending)
#     db_result = AsyncMock()
#     db_result.scalars().first.return_value = mock_transaction
#     db.execute.return_value = db_result

#     # Call the function being tested
#     transaction = await reject_transaction(db, transaction_id, current_user_id)

#     # Assert the transaction status is declined
#     assert transaction.status == Status.declined

# @pytest.mark.asyncio
# async def test_reject_transaction_transaction_not_found():
#     # Mock the database session to return None for the transaction
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = UUID("00000000-0000-0000-0000-000000000001")
#     current_user_id = UUID("00000000-0000-0000-0000-000000000002")
    
#     # Mock the query result
#     db_result = AsyncMock()
#     db_result.scalars().first.return_value = None

#     # Mock the execute method of the session to return the query result
#     db.execute.return_value = db_result

#     # Call the function being tested and expect HTTPException
#     with pytest.raises(HTTPException) as exc_info:
#         await reject_transaction(db, transaction_id, current_user_id)

#     # Assert HTTPException status code and detail message
#     assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
#     assert f"Transaction with id {transaction_id} not found." in exc_info.value.detail

# @pytest.mark.asyncio
# async def test_reject_transaction_not_pending():
#     # Mock the database session and query result
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = UUID("00000000-0000-0000-0000-000000000001")
#     current_user_id = UUID("00000000-0000-0000-0000-000000000002")
#     mock_transaction = Transaction(id=transaction_id, recipient_id=current_user_id, status=Status.confirmed)
#     db_result = AsyncMock()
#     db_result.scalars().first.return_value = mock_transaction
#     db.execute.return_value = db_result

#     # Call the function being tested and expect HTTPException
#     with pytest.raises(HTTPException) as exc_info:
#         await reject_transaction(db, transaction_id, current_user_id)

#     # Assert HTTPException status code and detail message
#     assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
#     assert "You can only reject pending transactions." in exc_info.value.detail

# @pytest.mark.asyncio
# async def test_reject_transaction_wrong_recipient():
#     # Mock the database session and query result
#     db = AsyncMock(spec=AsyncSession)
#     transaction_id = UUID("00000000-0000-0000-0000-000000000001")
#     current_user_id = UUID("00000000-0000-0000-0000-000000000002")
#     mock_transaction = Transaction(id=transaction_id, recipient_id=UUID("00000000-0000-0000-0000-000000000003"), status=Status.pending)
#     db_result = AsyncMock()
#     db_result.scalars().first.return_value = mock_transaction
#     db.execute.return_value = db_result

#     # Call the function being tested and expect HTTPException
#     with pytest.raises(HTTPException) as exc_info:
#         await reject_transaction(db, transaction_id, current_user_id)

#     # Assert HTTPException status code and detail message
#     assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
#     assert "You are not allowed to reject this transaction." in exc_info.value.detail


# @pytest.mark.asyncio
# async def test_deny_transaction_admin():
#     # Mock the database session and the user
#     db = AsyncMock(spec=AsyncSession)
#     current_user = User(id=UUID("00000000-0000-0000-0000-000000000001"), is_admin=True)
    
#     # Mock the query result to return a pending transaction
#     transaction_id = UUID("00000000-0000-0000-0000-000000000002")
#     db_result = AsyncMock()
#     db_result.scalars().first.return_value = Transaction(id=transaction_id, status=Status.pending)
#     db.execute.return_value = db_result

#     # Call the function being tested
#     response = await deny_transaction(db, current_user, transaction_id)

#     # Assert the response message
#     assert response == {"message": "Transaction declined."}
