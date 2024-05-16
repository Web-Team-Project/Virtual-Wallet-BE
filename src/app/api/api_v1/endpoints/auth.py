from fastapi import APIRouter, Depends
from starlette.requests import Request
from app.sql_app.models.models import User
from app.services.crud.user import get_current_user
from app.services.crud.auth import login as _login, auth_callback as _auth_callback, logout as _logout


router = APIRouter()


@router.get("/login")
async def login():
    return await _login()


@router.get("/auth/callback")
async def auth_callback_route(request: Request):
    return await _auth_callback(request)


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/logout")
async def logout_route(request: Request):
    return await _logout(request)