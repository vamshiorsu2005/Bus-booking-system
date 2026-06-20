from typing import AsyncGenerator, List, Optional
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis, RedisService
from app.core.security import decode_token
from app.core.exceptions import InvalidTokenException, PermissionDeniedException
from app.models.user import User
from app.services.user import user_service
from app.schemas.auth import TokenPayload

# OAuth2 scheme pointing to login route
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """FastAPI dependency to extract JWT, validate it, and return the User model with roles."""
    try:
        payload = decode_token(token, is_refresh=False)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "access":
            raise InvalidTokenException("Invalid token credentials")
        token_data = TokenPayload(sub=user_id, type=token_type)
    except jwt.JWTError:
        raise InvalidTokenException("Could not validate credentials")
    
    user = await user_service.get_user_by_id(db, user_id=token_data.sub)
    if not user:
        raise InvalidTokenException("User not found")
    if not user.is_active:
        raise InvalidTokenException("User is inactive")
    return user


class RoleRequired:
    """Dependency helper to enforce Role-Based Access Control (RBAC)."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_roles = [role.name for role in current_user.roles]
        
        # Super Admin bypasses all checks
        if "Super Admin" in user_roles:
            return current_user
            
        if not any(role in user_roles for role in self.allowed_roles):
            raise PermissionDeniedException(
                f"Requires one of the following roles: {', '.join(self.allowed_roles)}"
            )
        return current_user
