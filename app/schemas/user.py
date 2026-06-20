import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    roles: List[RoleOut] = []

    class Config:
        from_attributes = True
