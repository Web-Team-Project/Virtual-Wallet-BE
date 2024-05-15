from fastapi import HTTPException, status
from app.sql_app.models.user import User
from starlette.requests import Request


async def get_current_user(request: Request) -> User:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="User not authenticated.")
    return User(**user)