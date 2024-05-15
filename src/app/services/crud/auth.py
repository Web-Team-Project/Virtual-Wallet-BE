from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse


GOOGLE_CLIENT_ID = "1047295969598-97ot5u7518b43ng7tsi701iuq394m0vt.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080/api/v1/auth/callback"


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)


async def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)


async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Authorization code not found.")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
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

    request.session["user"] = userinfo
    return RedirectResponse("/swagger")


async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"message": "Successfully logged out"})