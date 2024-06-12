from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.schemas.contact import ContactCreate
from app.services.common.utils import get_current_user, process_request
from app.services.crud.contact import create_contact, delete_contact, read_contact, read_contacts
from app.sql_app.database import get_db
from app.sql_app.models.models import User


router = APIRouter()


@router.post("/contacts")
async def create(contact: ContactCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Create a new contact for the user. 
    The contact will be used to store the details of the user's contacts.
        Parameters:
            contact (ContactCreate): The contact data.
            current_user (User): The current user.
            db (AsyncSession): The database session.
        Returns:
            Contact: The created contact object.
    """
    async def _create_contact():
        return await create_contact(current_user, contact, db)

    return await process_request(_create_contact)


@router.get("/contacts")
async def view_contacts(skip: int = 0, limit: int = 100, 
                        current_user: User = Depends(get_current_user), 
                        db: AsyncSession = Depends(get_db), 
                        search: str = None):
    """
    View the contact list of the user.
        Parameters:
            skip (int): The number of contacts to skip.
            limit (int): The number of contacts to return.
            current_user (User): The current user.
            db (AsyncSession): The database session.
            search (str): The search term to filter the contacts.
        Returns:
            List[Contact]: The list of contacts.
    """
    async def _read_contacts():
        return await read_contacts(current_user, skip, limit, db, search)

    return await process_request(_read_contacts)


@router.get("/contacts/{contact_id}")
async def read(contact_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    View the details of a contact for the user.
        Parameters:
            contact_id (UUID): The ID of the contact to view.
            current_user (User): The current user.
            db (AsyncSession): The database session.
        Returns:
            Contact: The contact details.
    """
    async def _read_contact():
        return await read_contact(current_user, contact_id, db)
    
    return await process_request(_read_contact)


@router.delete("/contacts/{contact_id}")
async def delete(contact_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete a contact for the user. 
    The contact will be removed from the user's list of contacts.
        Parameters:
            contact_id (UUID): The ID of the contact to delete.
            current_user (User): The current user.
            db (AsyncSession): The database session.
        Returns:
            dict: A message confirming the deletion of the contact.
    """
    async def _delete_contact():
        return await delete_contact(current_user, contact_id, db)

    return await process_request(_delete_contact)