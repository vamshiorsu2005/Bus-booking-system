from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import DomainException

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade high-scale Bus Ticket Booking System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global handler for domain exceptions (business logic errors)
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    status_code = status.HTTP_400_BAD_REQUEST
    
    # Map domain errors to standard HTTP status codes
    if exc.code in ["INVALID_CREDENTIALS", "USER_DISABLED"]:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif exc.code == "SEAT_LOCK_EXPIRED":
        status_code = status.HTTP_410_GONE
    elif exc.code == "SEAT_UNAVAILABLE":
        status_code = status.HTTP_409_CONFLICT
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


# Health check endpoint
@app.get("/health", tags=["system"], status_code=status.HTTP_200_OK)
async def health_check():
    """Verify application health and availability."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV
    }

# Mount v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
