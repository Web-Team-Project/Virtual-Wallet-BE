from fastapi import HTTPException, status
from sqlalchemy import func, or_, update
from sqlalchemy.future import select
from app.core.config import get_settings
from app.schemas.user import UserBase
from app.sql_app.models.models import Card, User, Category, Contact, Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.sql_app.database import engine
from twilio.rest import Client


settings = get_settings()
client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


async def create_user(userinfo):
    """
    Create a new user using Google OAuth2 or update the existing one.
    Parameters:
        userinfo (dict): The user information.
    Returns:
        User: The created or updated user object.
    """
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == userinfo["email"]))
        user = result.scalars().first()
        if user:
            res = (update(User).where(User.email == userinfo["email"]).values(
                    sub=userinfo["sub"],
                    name=userinfo["name"],
                    given_name=userinfo["given_name"],
                    family_name=userinfo["family_name"],
                    picture=userinfo["picture"],
                    email_verified=userinfo["email_verified"],
                    locale=userinfo["locale"] if "locale" in userinfo else None,
                    is_active=True,
                    is_blocked=False,
                    is_admin=user.is_admin))
            await session.execute(res)
        else:
            new_user = User(
                sub=userinfo["sub"],
                name=userinfo["name"],
                given_name=userinfo["given_name"],
                family_name=userinfo["family_name"],
                picture=userinfo["picture"],
                email=userinfo["email"],
                email_verified=userinfo["email_verified"],
                locale=userinfo["locale"] if "locale" in userinfo else None,
                is_active=True,
                is_blocked=False,
                is_admin=False)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)


async def user_info(db: AsyncSession, current_user: UserBase):
    """
    View user's email and all associated cards, categories, contacts, and transactions.
        Parameters:
            db (AsyncSession): The database session.
            current_user (UserBase): The current user.
        Returns:
            dict: A dictionary with the user details.
    """
    result_cards = await db.execute(select(Card).where(Card.user_id == current_user.id))
    result_categories = await db.execute(select(Category).where(Category.user_id == current_user.id))
    result_contacts = await db.execute(select(Contact).where(Contact.user_id == current_user.id))
    result_transactions = await db.execute(
        select(Transaction).join(Card).where(Card.user_id == current_user.id))

    return {"email": current_user.email,
            "cards": result_cards.scalars().all(),
            "categories": result_categories.scalars().all(),
            "contacts": result_contacts.scalars().all(),
            "transactions": result_transactions.scalars().all(), }


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User:
    """
    View user's details by id.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
        Returns:
            User: The user details.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    return db_user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    View user's details by email.
        Parameters:
            email (str): The email of the user.
            db (AsyncSession): The database session.
        Returns:
            User: The user details.
    """
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    return db_user


async def get_user_by_phone(phone_number: str, db: AsyncSession):
    """
    View user's details by phone number.
        Parameters:
            phone_number (str): The phone number of the user.
            db (AsyncSession): The database session.
        Returns:
            User: The user details.
    """
    query = await db.execute(select(User).where(User.phone_number == phone_number))
    return query.scalar_one_or_none()


async def update_user_role(user_id: UUID, db: AsyncSession, current_user: User) -> User:
    """
    Update user's role to admin if authorized.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A dictionary with the message that the user role is updated successfully.
    """
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
    """
    Deactivate user's account if authorized. Unable to log in.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A dictionary with the message that the user is deactivated successfully.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return {"message": "User deactivated successfully."}


async def block_user(user_id: UUID, db: AsyncSession, current_user: User):
    """
    Block user's account if authorized. Unable to send or receive transactions.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            User: The blocked user object.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")
    user.is_blocked = True
    await db.commit()
    await db.refresh(user)
    return {"message": "User blocked successfully."}


async def unblock_user(user_id: UUID, db: AsyncSession, current_user: User):
    """
    Unblock user's account if authorized. Able to send and receive transactions.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            User: The unblocked user object.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    user.is_blocked = False
    await db.commit()
    await db.refresh(user)
    return {"message": "User unblocked successfully."}


async def search_users(db: AsyncSession, skip: int, limit: int, current_user: User, search: str = None):
    """
    View all users and their details. It also allows searching by email or phone number.
        Parameters:
            db (AsyncSession): The database session.
            skip (int): The number of users to skip.
            limit (int): The number of users to return.
            current_user (User): The current user.
            search (str): The search query.
        Returns:
            dict: A dictionary containing a list of users with their details and the total count of users.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to perform this action.")
    query = select(User)
    if search:
        query = query.where(or_(User.email.contains(search), User.phone_number.contains(search)))

    total_users = await db.execute(select(func.count()).select_from(query.subquery()))
    result = await db.execute(query.offset(skip).limit(limit))
    
    users = result.scalars().all()
    return {"users": users, "total": total_users.scalar()}