import random
from typing import Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.auth import Role
from app.models.operator import Operator
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import DomainException


class UserService:
    async def get_or_create_role(self, db: AsyncSession, role_name: str) -> Role:
        """Helper to get a role or create it if not present (self-seeding structure)."""
        query = select(Role).where(Role.name == role_name)
        result = await db.execute(query)
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name=role_name, description=f"Standard {role_name} role")
            db.add(role)
            await db.flush()
        return role

    async def create_user(self, db: AsyncSession, user_in: UserCreate, role_name: str = "Customer") -> User:
        """Create a new user, hashes password, and associates the role."""
        # Check if email is already taken
        existing_user = await user_repository.get_by_email(db, user_in.email)
        if existing_user:
            raise DomainException(f"User with email {user_in.email} already exists", code="EMAIL_ALREADY_EXISTS")

        # Resolve role
        role = await self.get_or_create_role(db, role_name)

        hashed_password = get_password_hash(user_in.password)
        user_data = {
            "email": user_in.email,
            "password_hash": hashed_password,
            "full_name": user_in.full_name,
            "phone_number": user_in.phone_number,
            "is_active": True,
            "is_verified": False,
        }

        # Create user
        user = User(**user_data)
        user.roles.append(role)
        db.add(user)
        await db.flush()

        # If role is Bus Operator, create the Operator profile
        if role_name == "Bus Operator":
            letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
            digits = "".join(random.choices("0123456789", k=4))
            chk = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            num = random.choice("0123456789")
            gst = f"29{letters}{digits}{chk}1Z{num}"

            operator_profile = Operator(
                user_id=user.id,
                company_name=f"{user.full_name} Travels",
                gst_number=gst,
                is_approved=True
            )
            db.add(operator_profile)
            await db.flush()

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: Any) -> Optional[User]:
        query = select(User).where(User.id == user_id).options(selectinload(User.roles))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, db: AsyncSession, user: User, user_in: UserUpdate) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        for field, value in user_data.items():
            setattr(user, field, value)
        db.add(user)
        await db.flush()
        return user


user_service = UserService()
