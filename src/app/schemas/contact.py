from pydantic import BaseModel
from uuid import UUID

class ContactBase(BaseModel):
    user_contact_id: UUID


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: UUID

    class Config:
        from_attributes = True