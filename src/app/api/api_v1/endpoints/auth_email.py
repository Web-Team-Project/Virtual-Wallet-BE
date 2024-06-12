from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.common.utils import process_request
from app.services.crud.auth_email import create_new_user, login, verify_email
from app.sql_app.database import get_db
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter()


@router.post("/users")
async def email_register(user: EmailUserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user using email and password.
        Parameters:
            user (EmailUserCreate): The user data.
            db (AsyncSession): The database session.
        Returns:
            dict: A message confirming the registration.
    """
    logging.info("Registering new user")
    async def _create_new_user():
        return await create_new_user(user, db)
    logging.info("User registered")
    return await process_request(_create_new_user)


@router.post("/token")
async def email_login(login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login the user using email and password.
        Parameters:
            login_request (LoginRequest): The login data.
            db (AsyncSession): The database session.
        Returns:
            dict: The user details and token.
    """
    logging.info("Logging in user")
    
    async def _email_login():
        return await login(login_request, db)
    logging.info("User logged in")
    return await process_request(_email_login)


@router.get("/verify")
async def email_verify(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify the email of the user using the token sent to the user's email.
        Parameters:
            token (str): The token sent to the user's email.
            db (AsyncSession): The database session.
        Returns:
            dict: A message confirming the verification.
    """
    logging.info("Verifying email")
    
    async def _verify_email():
        return await verify_email(token, db)
    
    logging.info("Email verified")
    return await process_request(_verify_email)