"""API Router"""
from fastapi import APIRouter

from app.api import auth, users, equipment, locations, qrcode

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(equipment.router)
api_router.include_router(locations.router)
api_router.include_router(qrcode.router)
