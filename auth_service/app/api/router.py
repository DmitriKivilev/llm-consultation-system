from fastapi import APIRouter
from .routes_auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
