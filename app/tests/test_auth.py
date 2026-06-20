import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.auth import Role


@pytest.mark.asyncio
async def test_register_customer(client: AsyncClient, db: AsyncSession):
    payload = {
        "email": "customer@example.com",
        "password": "testpassword123",
        "full_name": "Test Customer",
        "phone_number": "1234567890",
        "role": "Customer"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "Customer"

    # Verify user exists in DB
    query = select(User).where(User.email == payload["email"])
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.full_name == payload["full_name"]


@pytest.mark.asyncio
async def test_register_operator(client: AsyncClient, db: AsyncSession):
    payload = {
        "email": "operator@example.com",
        "password": "testpassword123",
        "full_name": "Test Operator",
        "phone_number": "0987654321",
        "role": "Operator"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["roles"][0]["name"] == "Bus Operator"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "password": "testpassword123",
        "full_name": "User One",
        "role": "Customer"
    }
    # Register first time
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    # Register second time
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first
    reg_payload = {
        "email": "login@example.com",
        "password": "testpassword123",
        "full_name": "Login User",
        "role": "Customer"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    # Register & Login
    reg_payload = {
        "email": "refresh@example.com",
        "password": "testpassword123",
        "full_name": "Refresh User"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "refresh@example.com",
        "password": "testpassword123"
    })
    tokens = login_res.json()

    # Refresh
    refresh_res = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    # Register & Login
    reg_payload = {
        "email": "profile@example.com",
        "password": "testpassword123",
        "full_name": "Profile User"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "profile@example.com",
        "password": "testpassword123"
    })
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Get profile
    profile_res = await client.get("/api/v1/users/me", headers=headers)
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile["email"] == reg_payload["email"]
    assert profile["full_name"] == reg_payload["full_name"]


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    # Register & Login
    reg_payload = {
        "email": "update@example.com",
        "password": "testpassword123",
        "full_name": "Before Update"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "update@example.com",
        "password": "testpassword123"
    })
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Update profile
    update_payload = {"full_name": "After Update", "phone_number": "9999999999"}
    update_res = await client.patch("/api/v1/users/me", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated_profile = update_res.json()
    assert updated_profile["full_name"] == "After Update"
    assert updated_profile["phone_number"] == "9999999999"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, db: AsyncSession):
    # Register & Login
    reg_payload = {
        "email": "logout@example.com",
        "password": "testpassword123",
        "full_name": "Logout User"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "logout@example.com",
        "password": "testpassword123"
    })
    tokens = login_res.json()

    # Logout
    logout_res = await client.post("/api/v1/auth/logout", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert logout_res.status_code == 200

    # Try refreshing again (should fail because refresh token is revoked)
    refresh_res = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert refresh_res.status_code == 401
