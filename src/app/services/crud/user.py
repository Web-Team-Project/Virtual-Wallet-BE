from fastapi import Depends, HTTPException, status
from app.sql_app.models.models import User
from starlette.requests import Request
from sqlalchemy.orm import Session


async def get_current_user(request: Request) -> User:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User not authenticated.")
    return User(**user)


async def update_user_role(user_id: int, role: str, db: Session, current_user: User = Depends(get_current_user)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="User does not have permission to update user role.")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    user.role = role
    db.commit()
    return user