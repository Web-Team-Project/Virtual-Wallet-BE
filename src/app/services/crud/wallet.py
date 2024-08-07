import uuid
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.sql_app.models.enumerate import Currency
from app.sql_app.models.models import User, Wallet


async def create_wallet(db: AsyncSession, user_id: UUID, currency: Currency) -> Wallet:
    """
    Create a new wallet for the user with the specified currency.
        Parameters:
            db (AsyncSession): The database session.
            user_id (UUID): The ID of the user.
            currency (Currency): The currency of the wallet.
        Returns:
            Wallet: The created wallet object.
    """

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    if not user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number not verified. Cannot create wallet.",
        )

    result = await db.execute(
        select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency)
    )
    wallet = result.scalars().first()
    if wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already exists for this user and currency.",
        )
    new_wallet = Wallet(
        id=uuid.uuid4(), user_id=user_id, balance=0.0, currency=currency
    )
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)
    return new_wallet


async def add_funds_to_wallet(
    db: AsyncSession, amount: float, current_user: User, currency: Currency
) -> Wallet:
    """Add funds to the user's wallet."""
    db_wallet = await db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id, Wallet.currency == currency
        )
    )
    db_wallet = db_wallet.scalars().first()
    if db_wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found."
        )
    db_wallet.balance += amount
    await db.commit()
    await db.refresh(db_wallet)
    return db_wallet


async def withdraw_funds_from_wallet(
    db: AsyncSession, current_user: User, amount: float, currency: Currency
) -> Wallet:
    """
    Withdraw funds from the user's wallet.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
            amount (float): The amount to withdraw.
            currency (Currency): The currency to withdraw.
        Returns:
            Wallet: The updated wallet object.
    """
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id, Wallet.currency == currency
        )
    )
    wallet = result.scalars().first()
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found."
        )
    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds."
        )
    wallet.balance -= amount
    await db.commit()
    await db.refresh(wallet)
    return wallet


async def check_balance(
    db: AsyncSession, current_user: User
) -> List[Tuple[float, Currency]]:
    """
    Check the balance of all wallets for the user.
        Parameters:
            db (AsyncSession): The database session.
            current_user (User): The current user.
        Returns:
            List[Tuple[float, Currency]]: A list of tuples with the balance and currency of the wallets.
    """
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallets = result.scalars().all()
    if not wallets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No wallets found."
        )
    return [(wallet.balance, wallet.currency) for wallet in wallets]
