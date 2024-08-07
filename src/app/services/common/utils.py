import logging
from datetime import datetime, timedelta
from typing import Any, Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer
from jose import jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.sql_app.database import engine
from app.sql_app.models.models import User

from .custom_response import WebErrorResponse

logger = logging.getLogger(__name__)


def create_access_token(data: dict) -> str:
    """
    Create an access token.
        Parameters:
            data (dict): The data to encode.
        Returns:
            str: The encoded token.
    """
    to_encode = data.copy()
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "yoursecretkey", algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode the access token.
        Parameters:
            token (str): The token to decode.
        Returns:
            dict: The decoded token.
    """
    user = jwt.decode(token, "yoursecretkey", algorithms=["HS256"])
    user.pop("exp")
    return user


async def get_current_user(request: Request) -> User:
    """
    Get the current user from the session.
        Parameters:
            request (Request): The request object.
        Returns:
            User: The current user.
    """
    user = request.cookies.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated."
        )
    current_user = decode_access_token(user)
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.email == current_user["email"])
        )
        db_user = result.scalars().first()
        if db_user:
            if db_user.email_verified is None or not db_user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not verified.",
                )
            if not db_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated.",
                )
            current_user["id"] = str(db_user.id)
            current_user["is_admin"] = db_user.is_admin
    return User(**current_user)


def generate_verification_token(email: str) -> str:
    """
    Create a token for email verification.
        Parameters:
            email (str): The email address.
        Returns:
            str: The token.
    """
    serializer = URLSafeTimedSerializer("yoursecretkey")
    return serializer.dumps(email, salt="email-verification-salt")


async def process_request(execute_fn: Callable) -> Any | JSONResponse:
    """
    Process the request and handle exceptions.
        Parameters:
            execute_fn (Callable): The function to execute.
        Returns:
            Any | JSONResponse: The result of the function or an error response.
    """
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
