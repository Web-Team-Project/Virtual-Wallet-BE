from fastapi import Depends, HTTPException, status, Request, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.crud.email_user import authenticate_user, register_with_email
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql_app.database import get_db


router = APIRouter()


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/users")
async def create_new_user(user: EmailUserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = await register_with_email(db, user.email, hashed_password, user.phone_number)
    return db_user


@router.post("/token")
async def login(request: Request, login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.session["user"] = {"id": str(user.id), "email": user.email, "phone_number": user.phone_number}
    return {"access_token": user.email, "token_type": "bearer"}