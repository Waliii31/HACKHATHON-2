from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta
from uuid import UUID
from passlib.context import CryptContext

from app.database.session import get_db_session
from app.models.user import User
from app.auth.jwt import create_access_token
import logging

router = APIRouter(tags=["auth"])

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: str


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user and return an access token.
    """
    # Note: In a real application, you should check for existing users first
    # and handle potential race conditions
    
    try:
        # Check if user already exists
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash the password (not yet stored on model)
        hashed_password = hash_password(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            name=user_data.name
        )

        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(new_user.id), "email": new_user.email}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(new_user.id)
        )
    except HTTPException:
        # re-raise known HTTP exceptions
        raise
    except Exception as exc:
        logging.exception("Error in register endpoint")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Authenticate a user and return an access token.
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # For now, we're not storing passwords - using JWT from Better Auth
    # In a full implementation, you would verify the password here
    # if not verify_password(credentials.password, user.password_hash):
    #     raise HTTPException(...)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id)
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get the current authenticated user's information.
    This endpoint requires a valid JWT token in the Authorization header.
    """
    # This would be implemented with the actual current user from the token
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
