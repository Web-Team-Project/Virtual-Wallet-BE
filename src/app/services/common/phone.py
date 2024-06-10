from fastapi import HTTPException, status
from app.core.config import get_settings
from app.schemas.user import UserBase
from app.services.crud.user import get_user_by_email
from app.sql_app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client


settings = get_settings()
client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


def send_verification_code(phone_number: str):
    """
    Send a verification code to the user's phone number.
    """
    try:
        verification = client.verify.v2.services(
            settings.VERIFY_SERVICE_SID).verifications.create(to=phone_number, channel="sms")
        print("Verification code sent successfully! SID:", verification.sid)
    except Exception as e:
        print("Failed to send verification code:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send verification code.")


def verify_code(phone_number: str, code: str):
    """
    Verify the code sent to the user's phone number.
        Parameters:
            phone_number (str): The phone number to verify.
            code (str): The verification code.
        Returns:
            bool: True if the code is approved, otherwise False.
    """
    try:
        verification_check = (
            client.verify.v2.services(
                settings.VERIFY_SERVICE_SID).verification_checks.create(to=phone_number, code=code))
        if verification_check.status == "approved":
            return True
        else:
            return False
    except Exception as e:
        print("Failed to verify code:", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify code.")


async def add_phone(phone_number: str, db: AsyncSession, current_user: User):
    """
    Add a phone number to the user's account if registered without one. The phone number must be unique.
        Parameters:
            phone_number (str): The phone number to add.
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            dict: A dictionary with the message that the phone number is added successfully.
    """
    user = await get_user_by_email(current_user.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.phone_number = phone_number
    user.phone_verified = False
    await db.commit()
    await db.refresh(user)

    send_verification_code(phone_number)
    return {"message": "Verification code sent to your phone."}


async def verify_phone(code: str, db: AsyncSession, current_user: UserBase):
    """
    Verify the phone number using the code sent to the user's phone.
        Parameters:
            code (str): The verification code.
            db (AsyncSession): The database session.
            current_user (UserBase): The current user.
        Returns:
            dict: A dictionary with the message that the phone number is verified successfully.
    """
    user = await get_user_by_email(current_user.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    phone_number = user.phone_number
    if not phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has no phone number registered.")

    if verify_code(phone_number, code):
        user.phone_verified = True
        await db.commit()
        await db.refresh(user)
        return {"message": "Phone number verified successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code.")