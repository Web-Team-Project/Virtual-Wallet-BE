from fastapi import HTTPException, status
from sqlalchemy import or_, select, update
from sqlalchemy.future import select
from app.schemas.user import UserBase
from app.sql_app.models.models import Card, User, Category, Contact, Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.sql_app.database import engine


async def create_user(userinfo, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == userinfo["email"]))
    user = result.scalars().first()
    if user:
        res = (
            update(User)
            .where(User.email == userinfo["email"])
            .values(
                sub=userinfo["sub"],
                name=userinfo["name"],
                given_name=userinfo["given_name"],
                family_name=userinfo["family_name"],
                picture=userinfo["picture"],
                email_verified=userinfo["email_verified"],
                locale=userinfo["locale"],
                is_active=True,
                is_blocked=False,
                is_admin=user.is_admin,
            )
        )
        await db.execute(res)
    else:
        new_user = User(
            sub=userinfo["sub"],
            name=userinfo["name"],
            given_name=userinfo["given_name"],
            family_name=userinfo["family_name"],
            picture=userinfo["picture"],
            email=userinfo["email"],
            email_verified=userinfo["email_verified"],
            locale=userinfo["locale"],
            is_active=True,
            is_blocked=False,
            is_admin=False,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)


async def user_info(db: AsyncSession, current_user: UserBase):
    """View user's email and all associated cards, categories, contacts, and transactions."""
    result_cards = await db.execute(select(Card).where(Card.user_id == current_user.id))
    result_categories = await db.execute(select(Category).where(Category.user_id == current_user.id))
    result_contacts = await db.execute(select(Contact).where(Contact.user_id == current_user.id))
    result_transactions = await db.execute(
        select(Transaction).join(Card).where(Card.user_id == current_user.id))

    return {"email": current_user.email,
            "cards": result_cards.scalars().all(),
            "categories": result_categories.scalars().all(),
            "contacts": result_contacts.scalars().all(),
            "transactions": result_transactions.scalars().all(),}


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User:
    """View user's details by id."""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    return db_user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """View user's details by email."""
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    return db_user


async def add_phone(phone_number, db: AsyncSession, current_user: User) -> User:
    """Add a phone number to the user's account if registered without one."""
    result = await db.execute(select(User).where(User.id == current_user.id))
    db_user = result.scalars().first()
    if db_user.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Phone number already taken.")
    db_user.phone_number = phone_number.phone_number
    await db.commit()
    await db.refresh(db_user)
    return {"message": "Phone number updated successfully."}


async def update_user_role(user_id: UUID, db: AsyncSession, current_user: User) -> User:
    """Update user's role to admin if authorized."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.is_admin = True
    await db.commit()
    await db.refresh(db_user)
    return {"message": "User role updated successfully."}


async def deactivate_user(user_id: UUID, db: AsyncSession, current_user: User) -> User:
    """Deactivate user's account if authorized. Unable to log in."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return {"message": "User deactivated successfully."}


async def block_user(user_id: UUID, db: AsyncSession, current_user: User):
    """Block user's account if authorized. Unable to send or receive transactions."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    db_user = await get_user_by_id(user_id, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.is_blocked = True
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def unblock_user(user_id: UUID, db: AsyncSession, current_user: User):
    """Unblock user's account if authorized. Able to send and receive transactions."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    db_user = await get_user_by_id(user_id, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.is_blocked = False
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def search_users(db: AsyncSession, skip: int, limit: int, current_user: User, search: str = None):
    """View all users and their details. It also allows searching by email or phone number."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action.")
    if search is None:
        result = await db.execute(select(User).offset(skip).limit(limit))
    else:
        result = await db.execute(select(User)
                                  .where(or_(User.email.contains(search), User.phone_number.contains(search)))
                                  .offset(skip).limit(limit))
    users = result.scalars().all()
    return users