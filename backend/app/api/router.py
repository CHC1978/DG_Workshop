"""API Router"""
from fastapi import APIRouter

from app.api import auth, users

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
