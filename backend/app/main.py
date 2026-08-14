"""
FastAPI Application Entrypoint for Fraud Detection & Financial Risk Analysis System.
Serves both REST API endpoints (/api/v1) and Unified React Frontend UI (/).
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure repository root is on sys.path for direct script execution
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db.models import User
from backend.app.core.security import get_password_hash
from backend.app.api.v1.router import api_router

DIST_DIR = BASE_DIR / "frontend" / "dist"

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Mount Static Assets & React Single Page Application (SPA)
if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path:
            file_path = DIST_DIR / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to the Fraud Detection & Financial Risk Analysis API",
            "docs": "/docs",
            "version": settings.VERSION,
            "api_v1": settings.API_V1_STR
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
