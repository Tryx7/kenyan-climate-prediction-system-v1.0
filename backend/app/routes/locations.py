from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.utils.kenya_locations import ALL_LOCATIONS, COUNTIES, TOWNS, CLIMATE_ZONES

router = APIRouter()

@router.get("/search")
async def search_locations(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search Kenyan locations with autocomplete"""
    q = q.lower()
    results = []

    for name, data in ALL_LOCATIONS.items():
        if q in name.lower():
            results.append({
                "name": name,
                "type": "county" if name in COUNTIES else "town",
                "coordinates": {"lat": data["lat"], "lon": data["lon"]},
                "elevation": data["elevation"],
                "region": data["region"],
                "climate_zone": CLIMATE_ZONES.get(data["region"], {})
            })

    # Sort by relevance (exact match first, then starts with, then contains)
    def sort_key(item):
        name_lower = item["name"].lower()
        if name_lower == q:
            return (0, name_lower)
        elif name_lower.startswith(q):
            return (1, name_lower)
        else:
            return (2, name_lower)

    results.sort(key=sort_key)
    return {"query": q, "results": results[:limit], "total": len(results)}

@router.get("/all")
async def get_all_locations(
    region: Optional[str] = Query(None, description="Filter by region"),
    type: Optional[str] = Query(None, description="Filter by type: county or town")
):
    """Get all Kenyan locations"""
    locations = []
    source = ALL_LOCATIONS

    if type == "county":
        source = COUNTIES
    elif type == "town":
        source = TOWNS

    for name, data in source.items():
        if region and data["region"] != region:
            continue

        locations.append({
            "name": name,
            "type": "county" if name in COUNTIES else "town",
            "coordinates": {"lat": data["lat"], "lon": data["lon"]},
            "elevation": data["elevation"],
            "region": data["region"],
            "climate_zone": CLIMATE_ZONES.get(data["region"], {})
        })

    return {"locations": locations, "total": len(locations)}

@router.get("/regions")
async def get_regions():
    """Get all climate regions"""
    return {
        "regions": [
            {
                "name": region,
                "avg_temperature": data["avg_temp"],
                "avg_rainfall": data["avg_rainfall"],
                "avg_humidity": data["humidity"],
                "rainfall_pattern": data["seasons"],
                "locations": [
                    name for name, loc in ALL_LOCATIONS.items() 
                    if loc["region"] == region
                ]
            }
            for region, data in CLIMATE_ZONES.items()
        ]
    }

@router.get("/{location}")
async def get_location_details(location: str):
    """Get detailed information about a location"""
    if location not in ALL_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")

    data = ALL_LOCATIONS[location]
    climate = CLIMATE_ZONES.get(data["region"], {})

    return {
        "name": location,
        "type": "county" if location in COUNTIES else "town",
        "coordinates": {"lat": data["lat"], "lon": data["lon"]},
        "elevation_meters": data["elevation"],
        "region": data["region"],
        "climate_profile": climate,
        "rainy_seasons": [
            {"name": "Long Rains (MAM)", "months": ["March", "April", "May"]},
            {"name": "Short Rains (OND)", "months": ["October", "November", "December"]}
        ] if climate.get("seasons") == "bimodal" else [
            {"name": "Main Rains", "months": ["April", "May", "June", "July", "August"]}
        ]
    }
