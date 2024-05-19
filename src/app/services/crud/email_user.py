from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.services.crud.user import get_user_by_email
from app.sql_app.models.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(email, db)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


async def register_with_email(db: AsyncSession, email: str, hashed_password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User already exists.")

    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_blocked": user.is_blocked,
            "is_admin": user.is_admin}