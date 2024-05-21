from fastapi import Depends, HTTPException, status, Request, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas.email_user import LoginRequest, User, UserInDB
from app.services.common.utils import get_current_user
from app.services.crud.email_user import authenticate_user
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crud.user import get_user_by_email
from app.sql_app.database import get_db


router = APIRouter()


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(email, db)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

@router.post("/token")
async def login(request: Request, login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.session['user'] = {'email': user.email}
    return {"access_token": user.email, "token_type": "bearer"}



@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")