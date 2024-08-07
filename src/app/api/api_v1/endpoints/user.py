from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import AddPhoneRequest, User, UserBase, VerifyPhoneRequest
from app.services.common.phone import add_phone, verify_phone
from app.services.common.utils import get_current_user, process_request
from app.services.crud.user import (
    block_user,
    deactivate_user,
    get_user_by_email,
    search_users,
    unblock_user,
    update_user_role,
    user_info,
)
from app.sql_app.database import get_db

router = APIRouter()


@router.get("/users/info")
async def get_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """
    Get the user's email and all associated cards, categories, contacts, and transactions.
        Parameters:
            db (AsyncSession): The database session.
            current_user (UserBase): The current user.
        Returns:
            dict: A dictionary with the user details.
    """
    user_details = await user_info(db, current_user)
    return user_details


@router.get("/users/{email}")
async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    """
    Get the user's details by email.
        Parameters:
            email (str): The email of the user.
            db (AsyncSession): The database session.
        Returns:
            User: The user details.
    """

    async def _get_user():
        return await get_user_by_email(email, db)

    return await process_request(_get_user)


@router.post("/users/phone")
async def add_phone_number(
    add_phone_request: AddPhoneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    phone_number = add_phone_request.phone_number
    """
    Add a phone number to the user's account if registered without one. The phone number must be unique.
        Parameters:
            phone_number (str): The phone number to add.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the addition.
    """

    async def _add_phone():
        return await add_phone(phone_number, db, current_user)

    return await process_request(_add_phone)


@router.post("/verify_phone")
async def verify_phone_endpoint(
    verify_phone_request: VerifyPhoneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """
    Verify the phone number of the user.
        Parameters:
            verify_phone_request (VerifyPhoneRequest): The verification code.
            db (AsyncSession): The database session.
            current_user (UserBase): The current user.
        Returns:
            dict: A message confirming the verification.
    """
    code = verify_phone_request.code

    async def _verify_phone():
        return await verify_phone(code, db, current_user)

    return await process_request(_verify_phone)


@router.put("/users/{user_id}/role")
async def update_role(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the role of the user.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the update.
    """

    async def _update_user_role():
        return await update_user_role(user_id, db, current_user)

    return await process_request(_update_user_role)


@router.delete("/users/{user_id}/deactivate")
async def deactivate(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivate the user's account when the current user is an admin.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the deactivation.
    """

    async def _deactivate_user():
        return await deactivate_user(user_id, db, current_user)

    return await process_request(_deactivate_user)


@router.put("/users/{user_id}/block")
async def block(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Block the user when the current user is an admin.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the block.
    """

    async def _block_user():
        return await block_user(user_id, db, current_user)

    return await process_request(_block_user)


@router.put("/users/{user_id}/unblock")
async def unblock(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unblock the user when the current user is an admin.
        Parameters:
            user_id (UUID): The ID of the user.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A message confirming the unblock.
    """

    async def _unblock_user():
        return await unblock_user(user_id, db, current_user)

    return await process_request(_unblock_user)


@router.get("/search/users")
async def search_all_users(
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search for all users by email or phone number.
        Parameters:
            search (str): The search query.
            skip (int): The number of users to skip.
            limit (int): The number of users to return.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            list: A list of users with their details.
    """

    async def _search_users():
        return await search_users(db, skip, limit, current_user, search)

    return await process_request(_search_users)
