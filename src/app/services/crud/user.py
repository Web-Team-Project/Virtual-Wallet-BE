from fastapi import Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.future import select
from app.schemas.user import UserBase
from app.services.common.utils import get_current_user
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
                    locale=userinfo["locale"]))
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
                role="user")
            session.add(new_user)
            await session.commit()
        return UserBase(**userinfo)


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    return db_user


async def update_user_role(user_id: UUID, role: str, db: AsyncSession, current_user: User = Depends(get_current_user)) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User does not have permission to update user role.")
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.role = role
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(email: str, db: AsyncSession):
    db_user = await get_user_by_email(email, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    await db.delete(db_user)
    await db.commit()
    return {"message": "User deleted successfully."}


async def block_user(email: str, db: AsyncSession):
    db_user = await get_user_by_email(email, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.is_blocked = True
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def unblock_user(email: str, db: AsyncSession):
    db_user = await get_user_by_email(email, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    db_user.is_blocked = False
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def search_users(db: AsyncSession, search: str) -> list[User]: # Do the same for cards, transactions etc if correct
    result = await db.execute(select(User).filter(User.email.contains(search)))
    users = result.scalars().all()
    return users