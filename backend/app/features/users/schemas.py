from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.features.users.domain import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    role: UserRole
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str
