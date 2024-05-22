from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.crud.user import get_user_by_email
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


async def register_with_email(db: AsyncSession, email: str, hashed_password: str, phone_number: str):
    user = await get_user_by_email(email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User already exists.")
    user = User(email=email, hashed_password=hashed_password, phone_number=phone_number)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id,
            "email": user.email,
            "phone_number": user.phone_number}


async def create_new_user(user: EmailUserCreate, db: AsyncSession):
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = await register_with_email(db, user.email, hashed_password, user.phone_number)
    return db_user


async def login(request: Request, login_request: LoginRequest, db: AsyncSession):
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.session["user"] = {"id": str(user.id), "email": user.email, "phone_number": user.phone_number}
    return {"access_token": user.email, "token_type": "bearer"}