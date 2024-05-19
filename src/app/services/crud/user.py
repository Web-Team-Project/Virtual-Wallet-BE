from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select, update
from sqlalchemy.future import select
from app.sql_app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.sql_app.database import engine


async def create_user(userinfo):
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
                    locale=userinfo["locale"],
                    is_active=True,
                    is_blocked=False,
                    is_admin=False,))
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
                locale=userinfo["locale"],
                is_active=True,
                is_blocked=False,
                is_admin=False,)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    return db_user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    return db_user


async def update_user_role(user_id: UUID, db: AsyncSession, current_user: User) -> User:
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
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to perform this action.")
    result = await db.execute(select(User)
                              .where(or_(User.email.contains(search), User.phone_number.contains(search)))
                              .offset(skip).limit(limit))
    users = result.scalars().all()
    return users