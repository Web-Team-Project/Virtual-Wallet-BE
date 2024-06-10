import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crud.auth_email import authenticate_user, register_with_email, verify_email, create_new_user, login, \
    _map_user
from app.schemas.email_user import EmailUserCreate, LoginRequest
from app.sql_app.models.models import User
from itsdangerous import SignatureExpired, BadSignature
from uuid import UUID, uuid4

@pytest.fixture
def db():
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock()))
    return db


@pytest.fixture
def mock_user():
    mock_user = MagicMock(spec=User)
    mock_user.hashed_password = "hashed_password"
    mock_user.email_verified = True
    return mock_user


@pytest.mark.asyncio
async def test_authenticate_user_with_valid_credentials(db, mock_user):
    mock_pwd_context = MagicMock()
    mock_pwd_context.verify = AsyncMock(return_value=True)

    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=mock_user)), \
         patch("app.services.crud.auth_email.pwd_context", new=mock_pwd_context):
        user = await authenticate_user(db, "user@example.com", "password")

    assert user == mock_user


@pytest.mark.asyncio
async def test_authenticate_user_with_unverified_email(db, mock_user):
    mock_user.email_verified = False

    with patch("app.services.crud.auth_email.pwd_context") as mock_pwd_context:
        mock_pwd_context.verify.return_value = True

        with patch("app.services.crud.auth_email.get_user_by_email") as mock_get_user_by_email:
            mock_get_user_by_email.return_value = mock_user

            with pytest.raises(HTTPException) as excinfo:
                await authenticate_user(db, "user@example.com", "password")

            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert excinfo.value.detail == "Email not verified. Please verify your email."


@pytest.mark.asyncio
async def test_register_with_email_new_user(db):
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=None)))

    email = "user@example.com"
    hashed_password = "hashed_password"

    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=None)), \
         patch("app.services.crud.auth_email.generate_verification_token", new=MagicMock(return_value="dummy_token")), \
         patch("app.services.crud.auth_email.send_verification_email", new=MagicMock()):
        result = await register_with_email(email, hashed_password, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    assert result["email"] == email


@pytest.mark.asyncio
async def test_register_with_email_existing_user(db, mock_user):
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=mock_user)))

    email = "user@example.com"
    hashed_password = "hashed_password"

    with pytest.raises(HTTPException) as excinfo:
        await register_with_email(email, hashed_password, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "User already exists."


@pytest.mark.asyncio
async def test_verify_email_with_valid_token(db, mock_user):
    mock_user.verification_token = "valid_token"

    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=mock_user)))

    token = "valid_token"
    email = "user@example.com"

    mock_serializer = MagicMock()
    mock_serializer.loads = MagicMock(return_value=email)

    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=mock_user)), \
         patch("app.services.crud.auth_email.URLSafeTimedSerializer", return_value=mock_serializer):
        result = await verify_email(token, db)

    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result == {"message": "Email verified successfully"}


@pytest.mark.asyncio
async def test_verify_email_with_invalid_token(db):
    token = "invalid_token"

    with pytest.raises(HTTPException) as excinfo:
        await verify_email(token, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Invalid verification link."

@pytest.mark.asyncio
async def test_verify_email_with_bad_signature_token(db):
    token = "bad_signature_token"
    serializer = MagicMock()
    serializer.loads.side_effect = BadSignature("Invalid token")

    with patch("app.services.crud.auth_email.URLSafeTimedSerializer", return_value=serializer):
        with pytest.raises(HTTPException) as excinfo:
            await verify_email(token, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Invalid verification link."

@pytest.mark.asyncio
async def test_verify_email_with_expired_token(db):
    token = "expired_token"
    serializer = MagicMock()
    serializer.loads.side_effect = SignatureExpired("Token expired")

    with patch("app.services.crud.auth_email.URLSafeTimedSerializer", return_value=serializer):
        with pytest.raises(HTTPException) as excinfo:
            await verify_email(token, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Verification link expired."

@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_password(db, mock_user):
    mock_pwd_context = MagicMock()
    mock_pwd_context.verify = MagicMock(return_value=False)

    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=mock_user)), \
            patch("app.services.crud.auth_email.pwd_context", new=mock_pwd_context):
        with pytest.raises(HTTPException) as excinfo:
            await authenticate_user(db, "user@example.com", "wrongpassword")

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Incorrect email or password."



@pytest.mark.asyncio
async def test_verify_email_with_no_user(db):
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=None)))

    token = "valid_token"
    with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException):
            await verify_email(token, db)


@pytest.mark.asyncio
async def test_create_new_user(db):
    user_data = EmailUserCreate(email="user@example.com", hashed_password="password")

    mock_user = {"email": user_data.email}
    with patch("app.services.crud.auth_email.register_with_email", new=AsyncMock(return_value=mock_user)):
        result = await create_new_user(user_data, db)

    assert result["email"] == user_data.email


@pytest.mark.asyncio
async def test_login_with_valid_credentials(db, mock_user):
    mock_user.email = "user@example.com"
    mock_user.password = "password"
    mock_user.email_verified = True

    login_request = LoginRequest(email="user@example.com", password="password")
    request = MagicMock()
    request.session = {}

    with patch("app.services.crud.auth_email.authenticate_user", new=AsyncMock(return_value=mock_user)), \
         patch("app.services.crud.auth_email.create_access_token", new=MagicMock(return_value="dummy_token")), \
         patch("app.services.crud.auth_email._map_user", new=MagicMock(return_value={"email": "user@example.com", "sub": "user_id"})):
        result = await login(login_request, db)

    assert result.body.decode() == '{"message":"Successfully logged in."}'
    assert result.status_code == 200


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(db):
    login_request = LoginRequest(email="user@example.com", password="wrongpassword")
    request = MagicMock()

    with patch("app.services.crud.auth_email.authenticate_user", new=AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as excinfo:
            await login(login_request, db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_verify_email_with_no_user(db):
    token = "valid_token"
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=AsyncMock(return_value=None)))

    with patch("app.services.crud.auth_email.URLSafeTimedSerializer") as mock_serializer:
        mock_serializer().loads = MagicMock(return_value="user@example.com")

        with patch("app.services.crud.auth_email.get_user_by_email", new=AsyncMock(return_value=None)):
            with pytest.raises(HTTPException) as excinfo:
                await verify_email(token, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Invalid verification token."


@pytest.mark.asyncio
async def test_login_with_unverified_email(db, mock_user):
    mock_user.email = "user@example.com"
    mock_user.password = "password"
    mock_user.email_verified = False

    login_request = LoginRequest(email="user@example.com", password="password")
    request = MagicMock()
    request.session = {}

    with patch("app.services.crud.auth_email.authenticate_user", new=AsyncMock(return_value=mock_user)):
        with pytest.raises(HTTPException) as excinfo:
            await login(login_request, db)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Email not verified. Please verify your email."


def test_map_user():
    user_id = uuid4()
    user = User(id=user_id, email="user@example.com", hashed_password="hashed_password", email_verified=True)
    mapped_user = _map_user(user)

    assert mapped_user["id"] == str(user.id)
    assert mapped_user["email"] == user.email
    assert mapped_user["sub"] == str(user.id)
    assert "hashed_password" not in mapped_user
    assert mapped_user["email_verified"] == user.email_verified
    assert "is_active" in mapped_user
    assert "is_admin" in mapped_user
    assert "is_blocked" in mapped_user
    assert "family_name" in mapped_user
    assert "given_name" in mapped_user
    assert "locale" in mapped_user
    assert "name" in mapped_user
    assert "phone_number" in mapped_user
    assert "picture" in mapped_user