from uuid import UUID

from pydantic import BaseModel


class ContactBase(BaseModel):
    user_contact_id: UUID


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: UUID

    class Config:
        from_attributes = True
