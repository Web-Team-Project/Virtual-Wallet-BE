from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.schemas.contact import ContactCreate
from app.services.common.utils import process_request
from app.services.crud.contact import create_contact, delete_contact, read_contact, read_contacts
from app.services.crud.user import get_current_user
from app.sql_app.database import get_db
from app.sql_app.models.models import User


router = APIRouter()


@router.post("/contacts")
async def create(contact: ContactCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    async def _create_contact():
        return await create_contact(current_user, contact, db)
    
    return await process_request(_create_contact)


@router.get("/contacts")
async def view_contacts(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    async def _read_contacts():
        return await read_contacts(current_user, skip, limit, db)
    
    return await process_request(_read_contacts)


@router.get("/contacts/{contact_id}")
async def read(contact_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    async def _read_contact():
        return await read_contact(current_user, contact_id, db)
    
    return await process_request(_read_contact)


@router.delete("/contacts/{contact_id}")
async def delete(contact_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    async def _delete_contact():
        return await delete_contact(current_user, contact_id, db)

    return await process_request(_delete_contact)