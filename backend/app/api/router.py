"""API Router"""
from fastapi import APIRouter

from app.api import auth, users, equipment, sub_equipment, locations, projects, qrcode, customers, rentals, calibrations, uploads, dashboard

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(equipment.router)
api_router.include_router(sub_equipment.router)
api_router.include_router(locations.router)
api_router.include_router(projects.router)
api_router.include_router(qrcode.router)
api_router.include_router(customers.router)
api_router.include_router(rentals.router)
api_router.include_router(calibrations.router)
api_router.include_router(uploads.router)
api_router.include_router(dashboard.router)
