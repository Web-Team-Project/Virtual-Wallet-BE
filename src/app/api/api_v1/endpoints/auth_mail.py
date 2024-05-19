# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi.responses import RedirectResponse
# from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.services.crud.auth_mail import create_user, authenticate_user, get_user_by_email
# from app.schemas.user import UserCreate, User
# from app.sql_app.database import get_db
# import logging
#
# router = APIRouter()
#
# SECRET_KEY = "your-secret-key"
#
# serializer = URLSafeTimedSerializer(SECRET_KEY)
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# @router.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     logger.info(f"Login attempt with email: {form_data.username}")
#     user = await authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         logger.warning("Incorrect email or password")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     session_token = serializer.dumps(user.email)
#     response = RedirectResponse(url="/api/v1/users/me")
#     response.set_cookie(key="session", value=session_token, httponly=True)
#     return response
#
# @router.post("/register", response_model=User)
# async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     existing_user = await get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
#     new_user = await create_user(db, user)
#     return new_user
#
# async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
#     session_token = request.cookies.get("session")
#     if not session_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     try:
#         email = serializer.loads(session_token, max_age=3600)
#     except (BadSignature, SignatureExpired):
#         raise HTTPException(status_code=401, detail="Invalid or expired session token")
#     user = await get_user_by_email(db, email)
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user
#
# @router.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
#
# @router.post("/logout")
# async def logout(request: Request):
#     response = RedirectResponse(url="/")
#     response.delete_cookie(key="session")
#     return response
#
