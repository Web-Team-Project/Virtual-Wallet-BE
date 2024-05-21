from typing import Callable, Any
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, status
import logging
from app.schemas.user import UserBase
from .custom_response import WebErrorResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.sql_app.database import engine
from app.sql_app.models.models import User


logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> User:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not authenticated.")
    async with AsyncSession(engine) as session:
        if user.get("email_verified"):
            result = await session.execute(select(User).where(User.email == user["email"]))
        else:
            result = await session.execute(select(User).where(User.email == user["email"], User.email_verified == None))
        
        db_user = result.scalars().first()
        if db_user:
            user["id"] = str(db_user.id)
            user["is_admin"] = db_user.is_admin
    request.session["user"] = user
    return User(**user)



async def process_request(execute_fn: Callable) -> Any | JSONResponse:
    try:
        return await execute_fn()
    except SQLAlchemyError as ex:
        logger.exception("Database.....")
        return WebErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ex,
        )
    except SyntaxError as ex:
        logger.exception("Syntax Error")
        return WebErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ex,
        )