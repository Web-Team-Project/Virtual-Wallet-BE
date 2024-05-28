from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from app.core.config import get_settings
from app.services.crud.user import create_user


settings = get_settings()


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)


async def login():
    """
    Redirect to Google OAuth2 login page.
    """
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)


async def auth_callback(request: Request):
    """
    Handle the callback from Google OAuth2.
        Parameters:
            request (Request): The request object.
        Returns:
            RedirectResponse: Redirects to the Swagger UI.
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Authorization code not found.")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_json = token_response.json()

    if "error" in token_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=token_json["error"])

    access_token = token_json["access_token"]
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with AsyncClient() as client:
        userinfo_response = await client.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()

    if "error" in userinfo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=userinfo["error"])

    await create_user(userinfo)

    request.session["user"] = userinfo
    return RedirectResponse("https://localhost:3000/home")


async def logout(request: Request):
    """
    Log out the user by removing the session.
        Parameters:
            request (Request): The request object.
        Returns:
            JSONResponse: A JSON response with the message that the user is logged out.
    """
    request.session.pop("user", None)
    return JSONResponse({"message": "Successfully logged out."})