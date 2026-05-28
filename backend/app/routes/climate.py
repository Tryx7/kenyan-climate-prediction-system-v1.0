from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from app.services.enso_service import ENSOService
from app.services.climate_service import ClimateService
from app.utils.kenya_locations import ALL_LOCATIONS

router = APIRouter()

@router.get("/enso/current")
async def get_current_enso():
    """Get current ENSO (El Nino/La Nina) status"""
    enso = ENSOService()
    return await enso.get_current_status()

@router.get("/enso/history")
async def get_enso_history(
    years: int = Query(10, ge=1, le=50),
    include_forecast: bool = Query(True)
):
    """Get historical ENSO data"""
    enso = ENSOService()
    return await enso.get_historical_data(years=years, include_forecast=include_forecast)

@router.get("/enso/impact/{location}")
async def get_enso_impact(location: str):
    """Get ENSO impact analysis for a specific location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    enso = ENSOService()
    climate = ClimateService()

    current_enso = await enso.get_current_status()
    location_risk = await climate.get_location_risk_assessment(location, current_enso)

    return {
        "location": location,
        "enso_status": current_enso,
        "risk_assessment": location_risk,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/seasonal/{location}")
async def get_seasonal_outlook(location: str):
    """Get seasonal climate outlook for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    climate = ClimateService()
    return await climate.get_seasonal_outlook(location)

@router.get("/anomalies/{location}")
async def get_climate_anomalies(
    location: str,
    period: str = Query("1y", description="Period: 1m, 3m, 6m, 1y, 5y")
):
    """Get climate anomalies for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    climate = ClimateService()
    return await climate.get_anomalies(location, period)
