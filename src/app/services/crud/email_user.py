from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.common.utils import generate_verification_token
from app.services.crud.user import get_user_by_email
from app.services.crud.verification import send_verification_email
from app.sql_app.models.models import User


SECRET_KEY = "yoursecretkey"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(email, db)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


async def register_with_email(email: str, hashed_password: str, phone_number: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")
    
    token = generate_verification_token(email)
    user = User(email=email, hashed_password=hashed_password, phone_number=phone_number, verification_token=token)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    verification_link = f"http://localhost:8080/swagger#/verify?token={token}"
    send_verification_email(user.email, verification_link)
    
    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
    }


async def verify_email(token: str, db: AsyncSession):
    serializer = URLSafeTimedSerializer("yoursecretkey")
    try:
        email = serializer.loads(token, salt="email-verification-salt")
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link expired.")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification link.")
    
    user = await get_user_by_email(email, db)
    if not user or user.verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")
    
    user.email_verified = True
    user.verification_token = None
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Email verified successfully"}


async def create_new_user(user: EmailUserCreate, db: AsyncSession):
    """Register a new user with email, password, and phone number."""
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = await register_with_email(user.email, hashed_password, user.phone_number, db)
    return db_user


async def login(request: Request, login_request: LoginRequest, db: AsyncSession):
    """User login with email and password. It creates a session for the user."""
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.session["user"] = {"id": str(user.id), "email": user.email, "phone_number": user.phone_number}
    return {"access_token": user.email, "token_type": "bearer"}