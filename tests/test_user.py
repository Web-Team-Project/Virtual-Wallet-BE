import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from sqlalchemy import select, or_
from src.app.sql_app.database import AsyncSessionLocal, Base, engine, get_db
from src.app.schemas.user import UserBase
from src.app.services.crud.user import create_user, user_info, get_user_by_email, get_user_by_id, get_user_by_phone, \
    update_user_role, deactivate_user, block_user, unblock_user, search_users
from src.app.sql_app.models.models import Card, Category, Contact, Transaction, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from fastapi import HTTPException, status

@pytest.fixture
def db():
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.scalar_one_or_none = AsyncMock()
    return db


@pytest.fixture
def mock_user():
    mock_user = MagicMock(spec=User)
    mock_user.id = uuid4()
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_user.given_name = "Test"
    mock_user.family_name = "User"
    mock_user.picture = "http://example.com/picture.jpg"
    mock_user.email_verified = True
    mock_user.locale = "en"
    mock_user.sub = "test-sub"
    return mock_user


@pytest.mark.asyncio
async def test_user_info(db, mock_user):
    user_base = UserBase(
        id=str(mock_user.id),  # Ensure id is a string if UserBase expects a string
        email=mock_user.email,
        name=mock_user.name,
        given_name=mock_user.given_name,
        family_name=mock_user.family_name,
        picture=mock_user.picture,
        email_verified=mock_user.email_verified,
        locale=mock_user.locale,
        sub=mock_user.sub
    )

    card = Card(id=uuid4(), user_id=mock_user.id, number="1234567812345678", card_holder="Test Holder",
                exp_date="12/24", cvv="123", design="Test Design")
    category = Category(id=uuid4(), user_id=mock_user.id, name="Test Category")
    contact = Contact(id=uuid4(), user_id=mock_user.id, user_contact_id=mock_user.id)
    transaction = Transaction(id=uuid4(), card_id=card.id, amount=100.0, currency="USD", timestamp=None,
                              category_id=category.id, status="pending", sender_id=mock_user.id,
                              recipient_id=mock_user.id,
                              wallet_id=uuid4())

    db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[card])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[category])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[contact])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[transaction]))))
    ]

    result = await user_info(db, user_base)

    assert result["email"] == user_base.email
    assert len(result["cards"]) == 1
    assert result["cards"][0].number == "1234567812345678"
    assert len(result["categories"]) == 1
    assert result["categories"][0].name == "Test Category"
    assert len(result["contacts"]) == 1
    assert result["contacts"][0].user_contact_id == mock_user.id
    assert len(result["transactions"]) == 1
    assert result["transactions"][0].amount == 100.0


@pytest.mark.asyncio
async def test_user_info_no_data(db, mock_user):
    user_base = UserBase(
        id=str(mock_user.id),  # Ensure id is a string if UserBase expects a string
        email=mock_user.email,
        name=mock_user.name,
        given_name=mock_user.given_name,
        family_name=mock_user.family_name,
        picture=mock_user.picture,
        email_verified=mock_user.email_verified,
        locale=mock_user.locale,
        sub=mock_user.sub
    )

    db.execute.side_effect = [
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))),
        MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    ]

    result = await user_info(db, user_base)

    assert result["email"] == user_base.email
    assert len(result["cards"]) == 0
    assert len(result["categories"]) == 0
    assert len(result["contacts"]) == 0
    assert len(result["transactions"]) == 0


@pytest.mark.asyncio
async def test_handle_commit_exception():
    userinfo = {...}
    db = MagicMock(spec=AsyncSession)
    db.commit = AsyncMock(side_effect=Exception("Commit failed"))
    with patch("app.services.crud.user.AsyncSession", return_value=db):
        with pytest.raises(Exception):
            await create_user(userinfo)


@pytest.mark.asyncio
async def test_get_user_by_id():
    db = AsyncMock(spec=AsyncSession)

    user_id = uuid4()
    user = User(id=user_id, name="Test User", email="test@example.com")

    user_mock_result = MagicMock()
    user_mock_result.scalars.return_value.first.return_value = user

    db.execute = AsyncMock(return_value=user_mock_result)

    returned_user = await get_user_by_id(user_id, db)

    assert returned_user == user


@pytest.mark.asyncio
async def test_get_user_by_email():
    db = AsyncMock(spec=AsyncSession)

    user_email = "test@example.com"
    user = User(id=uuid4(), name="Test User", email=user_email)

    user_mock_result = MagicMock()
    user_mock_result.scalars.return_value.first.return_value = user

    db.execute = AsyncMock(return_value=user_mock_result)

    returned_user = await get_user_by_email(user_email, db)

    assert returned_user == user


@pytest.mark.asyncio
async def test_get_user_by_phone():
    db = AsyncMock(spec=AsyncSession)

    user_phone_number = "1234567890"
    user = User(id=uuid4(), name="Test User", phone_number=user_phone_number)

    user_mock_result = MagicMock()
    user_mock_result.scalar_one_or_none.return_value = user

    db.execute = AsyncMock(return_value=user_mock_result)

    returned_user = await get_user_by_phone(user_phone_number, db)

    assert returned_user == user


@pytest.mark.asyncio
async def test_update_user_role_not_admin():
    db_mock = MagicMock(spec=AsyncSession)

    current_user = User(id=UUID("123e4567-e89b-12d3-a456-426614174000"), is_admin=False)

    with pytest.raises(HTTPException) as exc_info:
        await update_user_role(UUID("123e4567-e89b-12d3-a456-426614174001"), db_mock, current_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You are not authorized to perform this action."


@pytest.mark.asyncio
async def test_update_user_role_user_not_found():
    db_mock = MagicMock(spec=AsyncSession)

    current_user = User(id=UUID("123e4567-e89b-12d3-a456-426614174000"), is_admin=True)

    db_mock.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await update_user_role(UUID("123e4567-e89b-12d3-a456-426614174001"), db_mock, current_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found."


@pytest.mark.asyncio
async def test_update_user_role_success():
    db_mock = MagicMock(spec=AsyncSession)

    current_user = User(id=UUID("123e4567-e89b-12d3-a456-426614174000"), is_admin=True)

    user_to_update = User(id=UUID("123e4567-e89b-12d3-a456-426614174001"), is_admin=False)
    db_mock.get.return_value = user_to_update

    response = await update_user_role(UUID("123e4567-e89b-12d3-a456-426614174001"), db_mock, current_user)

    assert response == {"message": "User role updated successfully."}
    assert user_to_update.is_admin == True
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(user_to_update)


@pytest.mark.asyncio
async def test_deactivate_user_unauthorized():
    db_mock = MagicMock(spec=AsyncSession)

    current_user = User(id=UUID("123e4567-e89b-12d3-a456-426614174000"), is_admin=False)

    with pytest.raises(HTTPException) as exc_info:
        await deactivate_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db_mock, current_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You are not authorized to perform this action."


@pytest.mark.asyncio
async def test_deactivate_user_not_found(db, mock_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await deactivate_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found."


@pytest.mark.asyncio
async def test_deactivate_user_found(db, mock_user):
    user_to_deactivate = MagicMock(spec=User)
    user_to_deactivate.id = UUID("123e4567-e89b-12d3-a456-426614174001")
    user_to_deactivate.is_active = True

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_to_deactivate
    db.execute.return_value = mock_result

    result = await deactivate_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    assert result == {"message": "User deactivated successfully."}
    assert user_to_deactivate.is_active == False
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user_to_deactivate)


@pytest.mark.asyncio
async def test_block_user_not_authorized(db, mock_user):
    non_admin_user = MagicMock(spec=User)
    non_admin_user.is_admin = False

    with pytest.raises(HTTPException) as exc_info:
        await block_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, non_admin_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You are not authorized to perform this action."


@pytest.mark.asyncio
async def test_block_user_not_found(db, mock_user):
    # Mock query result with no user
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    # Call the function and check for the exception
    with pytest.raises(HTTPException) as exc_info:
        await block_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found."

@pytest.mark.asyncio
async def test_block_user_success(db, mock_user):
    user_to_block = MagicMock(spec=User)
    user_to_block.id = UUID("123e4567-e89b-12d3-a456-426614174001")
    user_to_block.is_blocked = False

    # Mock the result of the database query
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_to_block
    db.execute.return_value = mock_result

    # Call the function
    result = await block_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    # Assert the result
    assert result == {"message": "User blocked successfully."}
    assert user_to_block.is_blocked == True
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user_to_block)


@pytest.mark.asyncio
async def test_unblock_user_not_authorized(db, mock_user):
    non_admin_user = MagicMock(spec=User)
    non_admin_user.is_admin = False

    with pytest.raises(HTTPException) as exc_info:
        await unblock_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, non_admin_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You are not authorized to perform this action."

@pytest.mark.asyncio
async def test_unblock_user_not_found(db, mock_user):
    # Mock query result with no user
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    # Call the function and check for the exception
    with pytest.raises(HTTPException) as exc_info:
        await unblock_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    # Assert the exception details
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found."

@pytest.mark.asyncio
async def test_unblock_user_success(db, mock_user):
    user_to_unblock = MagicMock(spec=User)
    user_to_unblock.id = UUID("123e4567-e89b-12d3-a456-426614174001")
    user_to_unblock.is_blocked = True

    # Mock the result of the database query
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_to_unblock
    db.execute.return_value = mock_result

    # Call the function
    result = await unblock_user(UUID("123e4567-e89b-12d3-a456-426614174001"), db, mock_user)

    # Assert the result
    assert result == {"message": "User unblocked successfully."}
    assert user_to_unblock.is_blocked == False
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user_to_unblock)


@pytest.mark.asyncio
async def test_search_users_not_authorized(db, mock_user):
    non_admin_user = MagicMock(spec=User)
    non_admin_user.is_admin = False

    with pytest.raises(HTTPException) as exc_info:
        await search_users(db, skip=0, limit=10, current_user=non_admin_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You are not authorized to perform this action."


@pytest.mark.asyncio
async def test_search_users_no_search_term(db, mock_user):
    mock_user.is_admin = True
    users = [MagicMock(spec=User), MagicMock(spec=User)]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = users
    db.execute.return_value = mock_result

    result = await search_users(db, skip=0, limit=10, current_user=mock_user)

    assert result == users
    query = select(User).offset(0).limit(10)
    db.execute.assert_called_once()
    executed_query = db.execute.call_args[0][0]
    assert str(executed_query) == str(query)


@pytest.mark.asyncio
async def test_search_users_with_search_term(db, mock_user):
    mock_user.is_admin = True
    users = [MagicMock(spec=User), MagicMock(spec=User)]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = users
    db.execute.return_value = mock_result

    result = await search_users(db, skip=0, limit=10, current_user=mock_user, search="test")

    assert result == users
    query = select(User).where(or_(User.email.contains("test"), User.phone_number.contains("test"))).offset(0).limit(10)
    db.execute.assert_called_once()
    executed_query = db.execute.call_args[0][0]
    assert str(executed_query) == str(query)

