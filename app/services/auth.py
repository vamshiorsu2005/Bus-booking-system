from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.auth import RefreshToken, Session
from app.repositories.user import user_repository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import DomainException, InvalidTokenException
from app.schemas.auth import Token
from app.core.config import settings


class AuthService:
    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User:
        """Authenticate a user by email and password."""
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise DomainException("Invalid email or password", code="INVALID_CREDENTIALS")
        
        if not verify_password(password, user.password_hash):
            raise DomainException("Invalid email or password", code="INVALID_CREDENTIALS")
        
        if not user.is_active:
            raise DomainException("User account is disabled", code="USER_DISABLED")
            
        return user

    async def create_tokens(self, db: AsyncSession, user_id: str) -> Token:
        """Create access and refresh tokens, and store refresh token in database."""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        # Store refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(db_refresh_token)
        await db.flush()

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_session_tokens(self, db: AsyncSession, refresh_token: str) -> Token:
        """Validate and rotate refresh token, returning new access and refresh tokens."""
        try:
            payload = decode_token(refresh_token, is_refresh=True)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            if not user_id or token_type != "refresh":
                raise InvalidTokenException("Invalid token type")
        except Exception:
            raise InvalidTokenException("Expired or invalid refresh token")

        # Check in DB
        query = select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False
        )
        result = await db.execute(query)
        db_token = result.scalar_one_or_none()

        if not db_token or db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise InvalidTokenException("Refresh token expired or revoked")

        # Revoke old token
        db_token.is_revoked = True
        db.add(db_token)

        # Generate new pair
        return await self.create_tokens(db, user_id)

    async def revoke_refresh_token(self, db: AsyncSession, refresh_token: str) -> None:
        """Revoke a refresh token on logout."""
        query = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await db.execute(query)
        db_token = result.scalar_one_or_none()
        if db_token:
            db_token.is_revoked = True
            db.add(db_token)
            await db.flush()


auth_service = AuthService()
