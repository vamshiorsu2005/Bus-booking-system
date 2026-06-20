from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserOut, UserUpdate
from app.models.user import User
from app.services.user import user_service

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Retrieve details of the currently authenticated user."""
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_my_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update profile information of the currently authenticated user."""
    updated_user = await user_service.update_user(db, current_user, user_in)
    await db.commit()
    return updated_user
