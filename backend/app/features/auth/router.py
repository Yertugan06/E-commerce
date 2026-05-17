from fastapi import APIRouter, Depends

from app.core.dependencies import DBSessionDep, get_current_user
from app.features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.features.auth.use_cases import register_user, login_user
from app.features.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: DBSessionDep):
    return await register_user(db, body)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DBSessionDep):
    return await login_user(db, body)


@router.get("/me", response_model=UserRead)
async def me(current_user: UserRead | None = Depends(get_current_user)):
    return current_user
