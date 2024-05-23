from fastapi import Depends, Request, APIRouter, status, HTTPException
from fastapi import APIRouter, Depends
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.services.common.utils import process_request
from app.services.crud.email_user import create_new_user, login
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crud.user import get_user_by_email
from app.sql_app.database import get_db


router = APIRouter()


@router.post("/users")
async def email_register(user: EmailUserCreate, db: AsyncSession = Depends(get_db)):

    async def _create_new_user():
            return await create_new_user(user, db)
    
    return await process_request(_create_new_user)
    

@router.post("/token")
async def email_login(request: Request, login_request: LoginRequest, db: AsyncSession = Depends(get_db)):

    async def _email_login():
        return await login(request ,login_request, db)
    
    return await process_request(_email_login)


@router.get("/verify")
async def verify_email_endpoint(token: str, db: AsyncSession = Depends(get_db)):
    serializer = URLSafeTimedSerializer("your_secret_key")
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