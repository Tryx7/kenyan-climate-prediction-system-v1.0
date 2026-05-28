from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta

from app.services.database import get_db_pool
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data():
    """Get main dashboard analytics"""
    analytics = AnalyticsService()
    return await analytics.get_dashboard_summary()

@router.get("/predictions/trends")
async def get_prediction_trends(
    days: int = Query(30, ge=7, le=365)
):
    """Get prediction accuracy trends"""
    analytics = AnalyticsService()
    return await analytics.get_prediction_trends(days)

@router.get("/locations/popular")
async def get_popular_locations(
    limit: int = Query(10, ge=1, le=50)
):
    """Get most searched locations"""
    analytics = AnalyticsService()
    return await analytics.get_popular_locations(limit)

@router.get("/enso/trends")
async def get_enso_trends(
    years: int = Query(20, ge=5, le=50)
):
    """Get ENSO trend analysis"""
    analytics = AnalyticsService()
    return await analytics.get_enso_trends(years)

@router.get("/api/usage")
async def get_api_usage(
    days: int = Query(7, ge=1, le=90)
):
    """Get API usage statistics"""
    pool = await get_db_pool()
    since = datetime.utcnow() - timedelta(days=days)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT endpoint, COUNT(*) as requests, 
                      AVG(response_time_ms) as avg_response_time
               FROM api_logs 
               WHERE created_at > $1
               GROUP BY endpoint
               ORDER BY requests DESC""",
            since
        )

    return {"period_days": days, "endpoints": [dict(row) for row in rows]}
