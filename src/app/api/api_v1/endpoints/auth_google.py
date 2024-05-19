from fastapi import APIRouter, Depends
from starlette.requests import Request
from app.services.common.utils import process_request
from app.sql_app.models.models import User
from app.services.crud.user import get_current_user
from app.services.crud.auth import login, auth_callback, logout


router = APIRouter()


@router.get("/login")
async def login_route():

    async def _login():
        return await login()
    
    return await process_request(_login)


@router.get("/auth/callback")
async def auth_callback_route(request: Request):

    async def _auth_callback():
        return await auth_callback(request)
    
    return await process_request(_auth_callback)


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):

    async def _get_current_user():
        return current_user
    
    return await process_request(_get_current_user)


@router.get("/logout")
async def logout_route(request: Request):
    
    async def _logout():
        return await logout(request)
    
    return await process_request(_logout)