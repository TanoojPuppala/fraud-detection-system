"""
FastAPI Application Entrypoint for Fraud Detection & Financial Risk Analysis System.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db.models import User
from backend.app.core.security import get_password_hash
from backend.app.api.v1.router import api_router

# Initialize Database Tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Seeds default admin user if database is empty on application startup.
    """
    db: Session = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@fraudsys.com").first()
        if not admin_user:
            default_admin = User(
                email="admin@fraudsys.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            print("[+] Seeded default admin user (admin@fraudsys.com / admin123)")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Fraud Detection & Financial Risk Analysis API",
        "docs": "/docs",
        "version": settings.VERSION,
        "api_v1": settings.API_V1_STR
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
