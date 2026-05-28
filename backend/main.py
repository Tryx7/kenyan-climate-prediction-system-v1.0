from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import logging
import asyncio
from contextlib import asynccontextmanager

from app.routes import weather, climate, predictions, locations, alerts, analytics
from app.services.database import init_db, get_db_pool, close_db_pool  # <-- ADD close_db_pool
from app.services.cache import CacheService
from app.services.scheduler import start_scheduler, stop_scheduler
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting up Kenyan Climate Prediction System...")

    # Initialize database
    await init_db()

    # Initialize cache
    app.state.cache = CacheService()

    # Start background scheduler
    start_scheduler()

    logger.info("System startup complete!")
    yield

    # Shutdown
    logger.info("Shutting down system...")
    stop_scheduler()
    await close_db_pool()  # <-- ADD THIS LINE
    logger.info("System shutdown complete!")

app = FastAPI(
    title="Kenyan Climate & Weather Prediction API",
    description="AI-powered weather forecasting system analyzing El Niño and La Niña impacts on Kenya",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )
    return response

# Include routers
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(climate.router, prefix="/api/climate", tags=["Climate"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(locations.router, prefix="/api/locations", tags=["Locations"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "Kenyan Climate & Weather Prediction API",
        "version": "1.0.0",
        "status": "operational",
        "environment": ENVIRONMENT,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "cache": "connected",
            "ml_service": "operational"
        }
    }

@app.get("/api/ensostatus")
async def get_enso_status():
    """Get current El Ni\u00f1o / La Ni\u00f1a status"""
    from app.services.enso_service import ENSOService
    enso = ENSOService()
    return await enso.get_current_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
