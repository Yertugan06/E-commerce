from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import AUTH_TOKEN_INVALID
from app.features.users.repositories import get_user_by_id
from app.features.users.schemas import UserRead

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserRead:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AUTH_TOKEN_INVALID()
    except JWTError:
        raise AUTH_TOKEN_INVALID()

    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise AUTH_TOKEN_INVALID()

    return UserRead(
        id=user.id,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


DBSessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[UserRead, Depends(get_current_user)]
