from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timedelta
import httpx

from app.utils.kenya_locations import ALL_LOCATIONS
from app.services.ml_service import MLService
from app.services.cache import get_cache
from app.services.database import get_db_pool

router = APIRouter()

@router.get("/rainfall/{location}")
async def predict_rainfall(
    location: str,
    months: int = Query(3, ge=1, le=12),
    include_confidence: bool = Query(True)
):
    """Predict rainfall for a location"""
    cache = get_cache()
    cache_key = f"pred_rainfall_{location.lower()}_{months}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    ml = MLService()
    prediction = await ml.predict_rainfall(location, months)

    await cache.set(cache_key, prediction, ttl=3600)
    return prediction

@router.get("/drought/{location}")
async def predict_drought_risk(location: str):
    """Predict drought likelihood for a location"""
    cache = get_cache()
    cache_key = f"pred_drought_{location.lower()}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    ml = MLService()
    prediction = await ml.predict_drought(location)

    await cache.set(cache_key, prediction, ttl=3600)
    return prediction

@router.get("/flood/{location}")
async def predict_flood_risk(location: str):
    """Predict flood risk for a location"""
    cache = get_cache()
    cache_key = f"pred_flood_{location.lower()}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    ml = MLService()
    prediction = await ml.predict_flood(location)

    await cache.set(cache_key, prediction, ttl=3600)
    return prediction

@router.get("/temperature/{location}")
async def predict_temperature(
    location: str,
    months: int = Query(3, ge=1, le=12)
):
    """Predict temperature trends for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    ml = MLService()
    return await ml.predict_temperature(location, months)

@router.get("/comprehensive/{location}")
async def get_comprehensive_prediction(location: str):
    """Get comprehensive climate prediction for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    ml = MLService()
    return await ml.get_comprehensive_prediction(location)

@router.post("/retrain")
async def trigger_retrain(background_tasks: BackgroundTasks):
    """Trigger ML model retraining"""
    ml = MLService()
    background_tasks.add_task(ml.retrain_all_models)
    return {"message": "Model retraining started", "status": "in_progress"}

@router.get("/model-performance")
async def get_model_performance():
    """Get ML model performance metrics"""
    ml = MLService()
    return await ml.get_performance_metrics()
