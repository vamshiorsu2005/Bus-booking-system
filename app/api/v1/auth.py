from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import traceback

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token, RefreshTokenRequest
from app.schemas.user import UserOut
from app.services.user import user_service
from app.services.auth import auth_service
from app.core.exceptions import DomainException

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    register_in: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new customer or operator."""
    role_name = "Customer"
    if register_in.role.strip().lower() == "operator":
        role_name = "Bus Operator"
    elif register_in.role.strip().lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin registration is restricted."
        )
    
    user = await user_service.create_user(db, register_in, role_name=role_name)
    await db.commit()
    return user


@router.post("/login", response_model=Token)
async def login(
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate and issue JWT tokens."""
    user = await auth_service.authenticate(db, login_in.email, login_in.password)
    tokens = await auth_service.create_tokens(db, str(user.id))
    await db.commit()
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Rotate and refresh access tokens."""
    try:
        tokens = await auth_service.refresh_session_tokens(db, refresh_in.refresh_token)
        await db.commit()
        return tokens
    except Exception as e:
        print("Refresh Exception:")
        traceback.print_exc()
        raise


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout current session and revoke refresh token."""
    await auth_service.revoke_refresh_token(db, refresh_in.refresh_token)
    await db.commit()
    return {"message": "Successfully logged out"}

