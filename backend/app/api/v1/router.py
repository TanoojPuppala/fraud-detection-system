"""
Combined Router for API v1.
"""

from fastapi import APIRouter
from backend.app.api.v1 import auth, predict, analytics, explain, feedback, simulator

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(predict.router)
api_router.include_router(analytics.router)
api_router.include_router(explain.router)
api_router.include_router(feedback.router)
api_router.include_router(simulator.router)
