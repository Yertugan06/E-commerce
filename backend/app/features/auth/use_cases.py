from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password, get_password_hash
from app.features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.features.users.repositories import get_user_by_email, create_user
from app.features.users.schemas import UserRead


async def register_user(db: AsyncSession, request: RegisterRequest) -> TokenResponse:
    existing = await get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed = get_password_hash(request.password)
    user = await create_user(db, request.email, hashed)
    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ),
    )


async def login_user(db: AsyncSession, request: LoginRequest) -> TokenResponse:
    user = await get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ),
    )
