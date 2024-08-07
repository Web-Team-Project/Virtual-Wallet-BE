from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.contact import ContactCreate
from app.sql_app.models.models import Contact, User


async def create_contact(current_user: User, contact: ContactCreate, db: AsyncSession):
    """
    Create a new contact for the user.
        Parameters:
            current_user (User): The current user.
            contact (ContactCreate): The contact data.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the contact details.
    """
    user = await db.execute(select(User).filter(User.id == contact.user_contact_id))
    user = user.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    result = await db.execute(
        select(Contact).filter(
            Contact.user_id == current_user.id,
            Contact.user_contact_id == contact.user_contact_id,
        )
    )
    existing_contact = result.scalars().first()
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Contact already exists."
        )
    db_contact = Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return {
        "contact_id": db_contact.id,
        "contact_name": user.name,
        "contact_email": user.email,
    }


async def read_contacts(
    current_user: User, skip: int, limit: int, db: AsyncSession, search: str = None
):
    """
    View all contacts for the user. It also allows searching by email or phone number.
        Parameters:
            current_user (User): The current user.
            skip (int): The number of contacts to skip.
            limit (int): The number of contacts to return.
            db (AsyncSession): The database session.
            search (str): The search query.
        Returns:
            list: A list of contacts with their details.
    """
    query = select(Contact).filter(Contact.user_id == current_user.id)
    if search:
        query = query.filter(
            or_(User.email.contains(search), User.phone_number.contains(search))
        )
    result = await db.execute(query.distinct().offset(skip).limit(limit))
    contacts = result.scalars().all()
    response = []
    for contact in contacts:
        user = await db.execute(select(User).filter(User.id == contact.user_contact_id))
        user = user.scalars().first()
        response.append(
            {
                "contact_id": contact.id,
                "contact_name": user.name,
                "contact_email": user.email,
                "contact_phone_number": user.phone_number,
            }
        )
    return response


async def read_contact(current_user: User, contact_id: UUID, db: AsyncSession):
    """
    View contact's details by id.
        Parameters:
            current_user (User): The current user.
            contact_id (UUID): The ID of the contact.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the contact details.
    """
    result = await db.execute(
        select(Contact).filter(
            Contact.id == contact_id, Contact.user_id == current_user.id
        )
    )
    contact = result.scalars().first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found."
        )
    user = await db.execute(select(User).filter(User.id == contact.user_contact_id))
    user = user.scalars().first()
    return {
        "contact_id": contact.id,
        "contact_name": user.name,
        "contact_email": user.email,
    }


async def delete_contact(current_user: User, contact_id: UUID, db: AsyncSession):
    """
    Delete a contact by id.
        Parameters:
            current_user (User): The current user.
            contact_id (UUID): The ID of the contact.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the message that the contact has been deleted.
    """
    result = await db.execute(
        select(Contact).filter(
            Contact.id == contact_id, Contact.user_id == current_user.id
        )
    )
    contact = result.scalars().first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found."
        )
    await db.delete(contact)
    await db.commit()
    return {"message": "Contact has been deleted."}
