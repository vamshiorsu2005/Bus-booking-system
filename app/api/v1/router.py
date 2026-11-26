from fastapi import APIRouter
from app.api.v1 import auth, users, operator, search,cities

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(operator.router, prefix="/operator", tags=["operator"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(cities.router, prefix="/cities", tags=["cities"])

