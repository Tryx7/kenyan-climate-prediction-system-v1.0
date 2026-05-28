from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.database import get_db_pool
from app.utils.kenya_locations import ALL_LOCATIONS

router = APIRouter()

@router.get("/active")
async def get_active_alerts(
    location: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, description="low, medium, high, critical")
):
    """Get active climate alerts"""
    pool = await get_db_pool()

    query = """
        SELECT * FROM climate_alerts 
        WHERE is_active = true 
        AND (expires_at IS NULL OR expires_at > NOW())
    """
    params = []

    if location:
        query += " AND location = $1"
        params.append(location)

    if severity:
        query += f" AND severity = ${len(params) + 1}"
        params.append(severity)

    query += " ORDER BY created_at DESC"

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    alerts = [dict(row) for row in rows]
    return {"alerts": alerts, "total": len(alerts)}

@router.get("/history/{location}")
async def get_alert_history(
    location: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get alert history for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    pool = await get_db_pool()
    since = datetime.utcnow() - timedelta(days=days)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM climate_alerts 
               WHERE location = $1 AND created_at > $2 
               ORDER BY created_at DESC""",
            location, since
        )

    return {"location": location, "alerts": [dict(row) for row in rows]}

@router.post("/subscribe")
async def subscribe_to_alerts(
    location: str,
    alert_types: List[str],
    email: Optional[str] = None,
    phone: Optional[str] = None
):
    """Subscribe to climate alerts for a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    pool = await get_db_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO alert_subscriptions 
               (location, alert_types, email, phone, created_at)
               VALUES ($1, $2, $3, $4, NOW())
               ON CONFLICT (location, COALESCE(email, phone)) 
               DO UPDATE SET alert_types = $2, updated_at = NOW()""",
            location, alert_types, email, phone
        )

    return {"message": f"Subscribed to alerts for {location}"}
