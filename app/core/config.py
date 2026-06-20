import os
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    ENV: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Bus Ticket Booking System API"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "bus_booking"
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @model_validator(mode="before")
    @classmethod
    def assemble_db_and_services_urls(cls, data: dict) -> dict:
        # DB URL
        if not data.get("DATABASE_URL"):
            user = data.get("POSTGRES_USER", "postgres")
            password = data.get("POSTGRES_PASSWORD", "postgres")
            server = data.get("POSTGRES_SERVER", "localhost")
            port = data.get("POSTGRES_PORT", 5432)
            db = data.get("POSTGRES_DB", "bus_booking")
            data["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

        # Redis URL
        if not data.get("REDIS_URL"):
            host = data.get("REDIS_HOST", "localhost")
            port = data.get("REDIS_PORT", 6379)
            data["REDIS_URL"] = f"redis://{host}:{port}/0"

        # Celery URLs
        if not data.get("CELERY_BROKER_URL"):
            host = data.get("REDIS_HOST", "localhost")
            port = data.get("REDIS_PORT", 6379)
            data["CELERY_BROKER_URL"] = f"redis://{host}:{port}/1"
        if not data.get("CELERY_RESULT_BACKEND"):
            host = data.get("REDIS_HOST", "localhost")
            port = data.get("REDIS_PORT", 6379)
            data["CELERY_RESULT_BACKEND"] = f"redis://{host}:{port}/1"

        return data


settings = Settings()
