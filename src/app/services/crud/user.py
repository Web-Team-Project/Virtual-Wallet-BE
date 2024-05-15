from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.sql_app.models.user import User
from starlette.requests import Request
from sqlalchemy.orm import Session
from sql_app.models import User


async def get_current_user(request: Request) -> User:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User not authenticated.")
    return User(**user)


async def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


async def update_user(db: Session, user_id: int, user: UserCreate):
    user_db = await get_user(db, user_id)
    user_data = dict(user.__dict__)
    db.query(User).filter(User.id == user_id).update(user_data)
    db.commit()
    return user_db