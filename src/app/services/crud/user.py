from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.future import select
from app.sql_app.models.models import User
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(request: Request) -> User:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User not authenticated.")
    return User(**user)


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalars().first()
    return db_user


async def update_user_role(user_id: int, role: str, db: AsyncSession, current_user: User = Depends(get_current_user)) -> User:
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