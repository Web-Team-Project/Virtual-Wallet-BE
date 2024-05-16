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


async def update_user_role(user_id: int, role: str, db: AsyncSession, current_user: User = Depends(get_current_user)) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
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