from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.services.common.utils import get_current_user, process_request
from app.services.crud.auth_google import auth_callback, login, logout
from app.sql_app.models.models import User

router = APIRouter()


@router.get("/login")
async def login_route():
    """
    Login the user using Google OAuth2.0.
    Redirects to the Google OAuth2.0 login page.
        Parameters:
            request (Request): The request object.
        Returns:
            RedirectResponse: The redirect response to the Google OAuth2.0 login page.
    """

    async def _login():
        return await login()

    return await process_request(_login)


@router.get("/auth/callback")
async def auth_callback_route(request: Request):
    """
    Callback route for Google OAuth2.0.
    It is called after the user logs in using Google OAuth2.0.
    The user is authenticated and redirected to the home page.
        Parameters:
            request (Request): The request object.
        Returns:
            RedirectResponse: The redirect response to the home page.
    """

    async def _auth_callback():
        return await auth_callback(request)

    return await process_request(_auth_callback)


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Protected route that requires the user to be authenticated.
    Provides the user's information.
        Parameters:
            current_user (User): The current user.
        Returns:
            User: The current user object.
    """

    async def _get_current_user():
        return current_user

    return await process_request(_get_current_user)


@router.get("/logout")
async def logout_route():
    """
    Logout the user.
        Returns:
            RedirectResponse: The redirect response to the login page.
    """

    async def _logout():
        return await logout()

    return await process_request(_logout)
