from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.contact import ContactCreate
from app.schemas.user import User
from uuid import UUID
from app.sql_app.models.models import Contact


async def create_contact(current_user: User, contact: ContactCreate, db: AsyncSession):
    user = await db.execute(select(User).filter(User.id == contact.contact_user_id))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
        
    result = await db.execute(select(Contact).filter(Contact.user_id == current_user.id, Contact.contact_user_id == contact.contact_user_id))
    existing_contact = result.scalars().first()
    if existing_contact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Contact already exists.")
        
    db_contact = Contact(user_id=current_user.id, contact_user_id=user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


async def read_contacts(current_user: User, skip: int, limit: int, db: AsyncSession):
    result = await db.execute(select(Contact).filter(Contact.user_id == current_user.id).offset(skip).limit(limit))
    contacts = result.scalars().all()
    return contacts


async def read_contact(current_user: User, contact_id: UUID, db: AsyncSession):
    result = await db.execute(select(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id))
    contact = result.scalars().first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Contact not found.")
    return contact


async def delete_contact(current_user: User, contact_id: UUID, db: AsyncSession):
    result = await db.execute(select(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id))
    contact = result.scalars().first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Contact not found.")
    await db.delete(contact)
    await db.commit()
    return {"message": "Contact has been deleted."}