from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.common.utils import generate_verification_token
from app.services.crud.user import get_user_by_email
from app.services.common.verification import send_verification_email
from app.sql_app.models.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticate the user using email and password.
        Parameters:
            db (AsyncSession): The database session.
            email (str): The email of the user.
            password (str): The password of the user.
        Returns:
            User: The user object if the user is authenticated successfully.
    """
    user = await get_user_by_email(email, db)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Incorrect email or password.")
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email not verified. Please verify your email.")
    return user


async def register_with_email(email: str, hashed_password: str, db: AsyncSession):
    """
    Register a new user with email, password, and phone number.
        Parameters:
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.
            phone_number (str): The phone number of the user.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the user details.
    """
    user = await get_user_by_email(email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")

    token = generate_verification_token(email)
    user = User(email=email, hashed_password=hashed_password, verification_token=token)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    verification_link = f"https://virtual-wallet-87bx.onrender.com/api/v1/verify?token={token}"
    send_verification_email(user.email, verification_link)

    return {
        "id": user.id,
        "email": user.email,
    }


async def verify_email(token: str, db: AsyncSession):
    """
    Verify the email of the user using the token sent to the user's email.
        Parameters:
            token (str): The token sent to the user's email.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the message that the email is verified successfully.
    """
    serializer = URLSafeTimedSerializer("yoursecretkey")
    try:
        email = serializer.loads(token, salt="email-verification-salt")
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Verification link expired.")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid verification link.")
    user = await get_user_by_email(email, db)
    if not user or user.verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid verification token.")
    user.email_verified = True
    user.verification_token = None
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Email verified successfully"}


async def create_new_user(user: EmailUserCreate, db: AsyncSession):
    """
    Register a new user with email, password, and phone number.
        Parameters:
            user (EmailUserCreate): The user details.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the user details.
    """
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = await register_with_email(user.email, hashed_password, db)
    return db_user


async def login(request: Request, login_request: LoginRequest, db: AsyncSession):
    """
    User login with email and password. It creates a session for the user.
        Parameters:
            request (Request): The request object.
            login_request (LoginRequest): The login request.
            db (AsyncSession): The database session.
        Returns:
            dict: A dictionary with the access token and token type.
    """
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.session["user"] = {"id": str(user.id), "email": user.email, "phone_number": user.phone_number}
    return request.session["user"]