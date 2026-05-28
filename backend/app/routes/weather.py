from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import httpx
import asyncio

from app.utils.kenya_locations import ALL_LOCATIONS
from app.services.cache import get_cache
from app.services.database import get_db_pool

router = APIRouter()

OPEN_METEO_URL = "https://api.open-meteo.com/v1"

@router.get("/current/{location}")
async def get_current_weather(location: str):
    """Get current weather for a Kenyan location"""
    cache = get_cache()
    cache_key = f"weather_current_{location.lower()}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    loc_data = ALL_LOCATIONS.get(location)
    if not loc_data:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPEN_METEO_URL}/forecast",
            params={
                "latitude": loc_data["lat"],
                "longitude": loc_data["lon"],
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation", 
                           "weather_code", "wind_speed_10m", "wind_direction_10m",
                           "pressure_msl", "cloud_cover"],
                "timezone": "Africa/Nairobi"
            },
            timeout=30.0
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather service unavailable")

    data = response.json()
    result = {
        "location": location,
        "coordinates": {"lat": loc_data["lat"], "lon": loc_data["lon"]},
        "elevation": loc_data["elevation"],
        "region": loc_data["region"],
        "current": data.get("current", {}),
        "timestamp": datetime.utcnow().isoformat()
    }

    await cache.set(cache_key, result, ttl=600)  # 10 min cache
    return result

@router.get("/forecast/{location}")
async def get_weather_forecast(
    location: str,
    days: int = Query(7, ge=1, le=16),
    include_climate: bool = Query(True)
):
    """Get weather forecast with climate analysis"""
    cache = get_cache()
    cache_key = f"weather_forecast_{location.lower()}_{days}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    loc_data = ALL_LOCATIONS.get(location)
    if not loc_data:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPEN_METEO_URL}/forecast",
            params={
                "latitude": loc_data["lat"],
                "longitude": loc_data["lon"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                         "precipitation_probability_max", "weather_code", "wind_speed_10m_max",
                         "relative_humidity_2m_mean", "uv_index_max"],
                "forecast_days": days,
                "timezone": "Africa/Nairobi"
            },
            timeout=30.0
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather service unavailable")

    data = response.json()

    # Add climate context
    from app.services.climate_service import ClimateService
    climate_service = ClimateService()
    climate_context = await climate_service.get_climate_context(location)

    result = {
        "location": location,
        "coordinates": {"lat": loc_data["lat"], "lon": loc_data["lon"]},
        "region": loc_data["region"],
        "forecast_days": days,
        "daily": data.get("daily", {}),
        "climate_context": climate_context,
        "timestamp": datetime.utcnow().isoformat()
    }

    await cache.set(cache_key, result, ttl=1800)  # 30 min cache
    return result

@router.get("/historical/{location}")
async def get_historical_weather(
    location: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get historical weather data"""
    loc_data = ALL_LOCATIONS.get(location)
    if not loc_data:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPEN_METEO_URL}/archive",
            params={
                "latitude": loc_data["lat"],
                "longitude": loc_data["lon"],
                "start_date": start_date,
                "end_date": end_date,
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                         "relative_humidity_2m_mean", "wind_speed_10m_max", "pressure_msl_mean"],
                "timezone": "Africa/Nairobi"
            },
            timeout=60.0
        )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Historical data service unavailable")

    return {
        "location": location,
        "period": {"start": start_date, "end": end_date},
        "data": response.json().get("daily", {})
    }
