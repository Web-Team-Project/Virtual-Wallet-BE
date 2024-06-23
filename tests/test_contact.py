from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import ANY, AsyncMock, MagicMock
import pytest
from app.schemas.contact import ContactCreate
from app.services.crud.contact import create_contact, delete_contact, read_contact, read_contacts
from app.sql_app.models.models import User, Contact


@pytest.mark.asyncio
async def test_create_contact_user_not_found():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_data = ContactCreate(user_contact_id=uuid4())

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await create_contact(current_user, contact_data, db)
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "User not found."

    expected_query = select(User).filter(User.id == contact_data.user_contact_id)
    db.execute.assert_awaited_once()

    actual_query = db.execute.call_args[0][0]
    assert str(actual_query) == str(expected_query)


@pytest.mark.asyncio
async def test_create_contact_already_exists():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_data = ContactCreate(user_contact_id=uuid4())

    user_mock_result = MagicMock()
    user_mock_result.scalars.return_value.first.return_value = User(id=contact_data.user_contact_id)
    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = Contact(user_id=current_user.id, user_contact_id=contact_data.user_contact_id)

    db.execute = AsyncMock(side_effect=[user_mock_result, contact_mock_result])

    with pytest.raises(HTTPException) as excinfo:
        await create_contact(current_user, contact_data, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Contact already exists."

    expected_user_query = select(User).filter(User.id == contact_data.user_contact_id)
    expected_contact_query = select(Contact).filter(Contact.user_id == current_user.id, Contact.user_contact_id == contact_data.user_contact_id)

    db.execute.assert_awaited()

    actual_user_query = db.execute.call_args_list[0][0][0]
    actual_contact_query = db.execute.call_args_list[1][0][0]
    assert str(actual_user_query) == str(expected_user_query)
    assert str(actual_contact_query) == str(expected_contact_query)

    
@pytest.mark.asyncio
async def test_create_contact_success():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_data = ContactCreate(user_contact_id=uuid4())

    user_mock_result = MagicMock()
    user_mock_result.scalars.return_value.first.return_value = User(id=contact_data.user_contact_id, name="Contact User", email="contactuser@example.com")   
    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = None
    db.execute = AsyncMock(side_effect=[user_mock_result, contact_mock_result])

    db_contact = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=contact_data.user_contact_id)
    db.add = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock(side_effect=lambda instance: setattr(instance, 'id', db_contact.id))

    response = await create_contact(current_user, contact_data, db)

    assert response == {
        "contact_id": db_contact.id,
        "contact_name": "Contact User",
        "contact_email": "contactuser@example.com"
    }


@pytest.mark.asyncio
async def test_read_contacts_no_search():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_1 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    contact_2 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    
    user_1 = User(id=contact_1.user_contact_id, name="User 1", email="user1@example.com", phone_number="1234567890")
    user_2 = User(id=contact_2.user_contact_id, name="User 2", email="user2@example.com", phone_number="0987654321")
    
    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.all.return_value = [contact_1, contact_2]
    
    user_mock_result_1 = MagicMock()
    user_mock_result_1.scalars.return_value.first.return_value = user_1
    
    user_mock_result_2 = MagicMock()
    user_mock_result_2.scalars.return_value.first.return_value = user_2
    
    db.execute = AsyncMock(side_effect=[contact_mock_result, user_mock_result_1, user_mock_result_2])
    
    response = await read_contacts(current_user, skip=0, limit=10, db=db)
    
    assert response == [
        {"contact_id": contact_1.id, "contact_name": user_1.name, "contact_email": user_1.email, "contact_phone_number": user_1.phone_number},
        {"contact_id": contact_2.id, "contact_name": user_2.name, "contact_email": user_2.email, "contact_phone_number": user_2.phone_number},
    ]


@pytest.mark.asyncio
async def test_read_contacts_with_search():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_1 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    
    user_1 = User(id=contact_1.user_contact_id, name="User 1", email="user1@example.com", phone_number="1234567890")
    
    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.all.return_value = [contact_1]
    
    user_mock_result_1 = MagicMock()
    user_mock_result_1.scalars.return_value.first.return_value = user_1
    
    db.execute = AsyncMock(side_effect=[contact_mock_result, user_mock_result_1])
    
    response = await read_contacts(current_user, skip=0, limit=10, db=db, search="user1")
    
    assert response == [
        {"contact_id": contact_1.id, "contact_name": user_1.name, "contact_email": user_1.email, "contact_phone_number": user_1.phone_number},
    ]


@pytest.mark.asyncio
async def test_read_contacts_pagination():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_1 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    contact_2 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    contact_3 = Contact(id=uuid4(), user_id=current_user.id, user_contact_id=uuid4())
    
    user_1 = User(id=contact_1.user_contact_id, name="User 1", email="user1@example.com", phone_number="1234567890")
    user_2 = User(id=contact_2.user_contact_id, name="User 2", email="user2@example.com", phone_number="0987654321")
    user_3 = User(id=contact_3.user_contact_id, name="User 3", email="user3@example.com", phone_number="1122334455")
    
    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.all.return_value = [contact_2, contact_3]
    
    user_mock_result_1 = MagicMock()
    user_mock_result_1.scalars.return_value.first.return_value = user_2
    
    user_mock_result_2 = MagicMock()
    user_mock_result_2.scalars.return_value.first.return_value = user_3
    
    db.execute = AsyncMock(side_effect=[contact_mock_result, user_mock_result_1, user_mock_result_2])
    
    response = await read_contacts(current_user, skip=1, limit=2, db=db)
    
    assert response == [
        {"contact_id": contact_2.id, "contact_name": user_2.name, "contact_email": user_2.email, "contact_phone_number": user_2.phone_number},
        {"contact_id": contact_3.id, "contact_name": user_3.name, "contact_email": user_3.email, "contact_phone_number": user_3.phone_number},
    ]


@pytest.mark.asyncio
async def test_read_contact_success():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_id = uuid4()
    contact = Contact(id=contact_id, user_id=current_user.id, user_contact_id=uuid4())
    user = User(id=contact.user_contact_id, name="Contact User", email="contact@example.com")

    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = contact
    
    user_mock_result = MagicMock()
    user_mock_result.scalars.return_value.first.return_value = user
    
    db.execute = AsyncMock(side_effect=[contact_mock_result, user_mock_result])
    
    response = await read_contact(current_user, contact_id, db)
    
    assert response == {
        "contact_id": contact.id,
        "contact_name": user.name,
        "contact_email": user.email
    }


@pytest.mark.asyncio
async def test_read_contact_not_found():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_id = uuid4()

    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = None
    
    db.execute = AsyncMock(return_value=contact_mock_result)
    
    with pytest.raises(HTTPException) as excinfo:
        await read_contact(current_user, contact_id, db)
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Contact not found."


@pytest.mark.asyncio
async def test_read_contact_different_user():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_id = uuid4()
    contact = Contact(id=contact_id, user_id=uuid4(), user_contact_id=uuid4())

    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=contact_mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await read_contact(current_user, contact_id, db)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Contact not found."


@pytest.mark.asyncio
async def test_delete_contact_not_found():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_id = uuid4()

    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = None

    db.execute = AsyncMock(return_value=contact_mock_result)

    with pytest.raises(HTTPException) as excinfo:
        await delete_contact(current_user, contact_id, db)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Contact not found."


@pytest.mark.asyncio
async def test_delete_contact_success():
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=uuid4())
    contact_id = uuid4()
    contact = Contact(id=contact_id, user_id=current_user.id, user_contact_id=uuid4())

    contact_mock_result = MagicMock()
    contact_mock_result.scalars.return_value.first.return_value = contact

    db.execute = AsyncMock(return_value=contact_mock_result)
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    response = await delete_contact(current_user, contact_id, db)

    db.execute.assert_called_once_with(ANY)
    db.delete.assert_called_once_with(contact)
    db.commit.assert_called_once()

    assert response == {"message": "Contact has been deleted."}