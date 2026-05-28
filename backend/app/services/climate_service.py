from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
import logging

from app.utils.kenya_locations import ALL_LOCATIONS, CLIMATE_ZONES
from app.services.enso_service import ENSOService

logger = logging.getLogger(__name__)

class ClimateService:
    """Service for climate analysis and risk assessment"""

    def __init__(self):
        self.enso_service = ENSOService()

    async def get_climate_context(self, location: str) -> Dict:
        """Get climate context for a location"""
        loc_data = ALL_LOCATIONS[location]
        zone = CLIMATE_ZONES.get(loc_data["region"], {})

        # Get current ENSO status
        enso = await self.enso_service.get_current_status()

        # Determine climate risks based on ENSO and location
        risks = self._assess_climate_risks(location, enso, zone)

        return {
            "location": location,
            "region": loc_data["region"],
            "elevation": loc_data["elevation"],
            "climate_zone": zone,
            "current_enso": {
                "phase": enso.get("current_phase"),
                "severity": enso.get("severity"),
                "oni": enso.get("oni_value")
            },
            "seasonal_risks": risks,
            "rainfall_pattern": zone.get("seasons", "bimodal"),
            "typical_rainy_seasons": self._get_rainy_seasons(zone.get("seasons", "bimodal"))
        }

    def _assess_climate_risks(self, location: str, enso: Dict, zone: Dict) -> List[Dict]:
        """Assess climate risks based on ENSO phase and location"""
        phase = enso.get("current_phase", "Neutral")
        region = ALL_LOCATIONS[location]["region"]

        risks = []

        # Kenya-specific ENSO impacts
        if phase == "El Nino":
            if region in ["Coastal", "Western", "Central Highlands"]:
                risks.append({
                    "type": "heavy_rainfall",
                    "risk_level": "high",
                    "description": "Above-normal rainfall expected during OND season. Risk of flooding and landslides.",
                    "affected_seasons": ["October-November-December"],
                    "confidence": 0.75
                })
            if region in ["Eastern", "North Eastern", "Turkana"]:
                risks.append({
                    "type": "temperature_anomaly",
                    "risk_level": "medium",
                    "description": "Warmer than normal temperatures expected. Increased evapotranspiration.",
                    "affected_seasons": ["Year-round"],
                    "confidence": 0.65
                })

        elif phase == "La Nina":
            if region in ["Eastern", "North Eastern", "Turkana", "Coastal"]:
                risks.append({
                    "type": "drought",
                    "risk_level": "high",
                    "description": "Below-normal rainfall expected. Risk of drought conditions and water scarcity.",
                    "affected_seasons": ["March-May", "October-December"],
                    "confidence": 0.70
                })
            if region in ["Central Highlands", "Rift Valley"]:
                risks.append({
                    "type": "frost",
                    "risk_level": "medium",
                    "description": "Cooler temperatures may increase frost risk in highland areas.",
                    "affected_seasons": ["June-August"],
                    "confidence": 0.55
                })

        else:  # Neutral
            risks.append({
                "type": "normal_variability",
                "risk_level": "low",
                "description": "Near-normal rainfall expected. Standard agricultural practices recommended.",
                "affected_seasons": ["Year-round"],
                "confidence": 0.60
            })

        # Add region-specific baseline risks
        if region in ["Turkana", "North Eastern"]:
            risks.append({
                "type": "chronic_drought",
                "risk_level": "medium",
                "description": "Arid/semi-arid region with inherent drought vulnerability.",
                "affected_seasons": ["Year-round"],
                "confidence": 0.80
            })

        if region == "Western":
            risks.append({
                "type": "flooding",
                "risk_level": "medium",
                "description": "High rainfall region with potential for river flooding.",
                "affected_seasons": ["March-May", "October-December"],
                "confidence": 0.70
            })

        return risks

    def _get_rainy_seasons(self, pattern: str) -> List[Dict]:
        """Get rainy season information"""
        if pattern == "bimodal":
            return [
                {
                    "name": "Long Rains (MAM)",
                    "months": ["March", "April", "May"],
                    "typical_rainfall_mm": "200-400",
                    "agricultural_importance": "Primary planting season for maize and beans"
                },
                {
                    "name": "Short Rains (OND)",
                    "months": ["October", "November", "December"],
                    "typical_rainfall_mm": "150-300",
                    "agricultural_importance": "Secondary planting season"
                }
            ]
        else:
            return [
                {
                    "name": "Main Rains",
                    "months": ["April", "May", "June", "July", "August"],
                    "typical_rainfall_mm": "100-250",
                    "agricultural_importance": "Single planting season"
                }
            ]

    async def get_location_risk_assessment(self, location: str, enso_status: Dict) -> Dict:
        """Get detailed risk assessment for a location"""
        loc_data = ALL_LOCATIONS[location]
        zone = CLIMATE_ZONES.get(loc_data["region"], {})

        risks = self._assess_climate_risks(location, enso_status, zone)

        # Calculate overall risk score
        risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_score = sum(risk_scores.get(r["risk_level"], 1) for r in risks)
        max_score = len(risks) * 4

        if max_score > 0:
            normalized = total_score / max_score
            if normalized < 0.25:
                overall = "Low"
            elif normalized < 0.5:
                overall = "Medium"
            elif normalized < 0.75:
                overall = "High"
            else:
                overall = "Critical"
        else:
            overall = "Low"

        return {
            "overall_risk": overall,
            "risk_score": round(normalized * 100, 1) if max_score > 0 else 0,
            "detailed_risks": risks,
            "recommendations": self._get_recommendations(risks, loc_data["region"])
        }

    def _get_recommendations(self, risks: List[Dict], region: str) -> List[str]:
        """Get climate adaptation recommendations"""
        recommendations = []

        risk_types = [r["type"] for r in risks]

        if "drought" in risk_types or "chronic_drought" in risk_types:
            recommendations.extend([
                "Implement water harvesting and storage systems",
                "Plant drought-resistant crop varieties",
                "Practice conservation agriculture techniques",
                "Develop community water management plans"
            ])

        if "heavy_rainfall" in risk_types or "flooding" in risk_types:
            recommendations.extend([
                "Ensure proper drainage systems are in place",
                "Plant cover crops to prevent soil erosion",
                "Elevate critical infrastructure above flood levels",
                "Develop early warning systems for flash floods"
            ])

        if "temperature_anomaly" in risk_types:
            recommendations.extend([
                "Adjust planting dates to avoid extreme heat periods",
                "Use shade nets for sensitive crops",
                "Increase irrigation frequency during hot spells"
            ])

        if not recommendations:
            recommendations = [
                "Monitor weather forecasts regularly",
                "Maintain standard agricultural practices",
                "Keep emergency preparedness plans updated"
            ]

        return recommendations

    async def get_seasonal_outlook(self, location: str) -> Dict:
        """Get seasonal climate outlook"""
        enso = await self.enso_service.get_current_status()
        loc_data = ALL_LOCATIONS[location]
        zone = CLIMATE_ZONES.get(loc_data["region"], {})

        current_month = datetime.now().month

        # Determine current season
        if current_month in [3, 4, 5]:
            current_season = "MAM (Long Rains)"
            next_season = "JJA (Dry/Cool)"
        elif current_month in [6, 7, 8]:
            current_season = "JJA (Dry/Cool)"
            next_season = "SON (Short Rains)"
        elif current_month in [9, 10, 11]:
            current_season = "SON (Short Rains)"
            next_season = "DJF (Hot/Dry)"
        else:
            current_season = "DJF (Hot/Dry)"
            next_season = "MAM (Long Rains)"

        return {
            "location": location,
            "current_season": current_season,
            "next_season": next_season,
            "enso_influence": enso.get("current_phase"),
            "outlook": self._generate_outlook(location, current_season, enso),
            "historical_comparison": await self._get_historical_comparison(location)
        }

    def _generate_outlook(self, location: str, season: str, enso: Dict) -> str:
        """Generate seasonal outlook text"""
        phase = enso.get("current_phase", "Neutral")
        region = ALL_LOCATIONS[location]["region"]

        if "MAM" in season:
            if phase == "El Nino":
                return f"Above-normal rainfall expected for {location} during the Long Rains. Good planting conditions but watch for potential flooding."
            elif phase == "La Nina":
                return f"Below-normal rainfall likely for {location}. Drought risk elevated. Consider drought-resistant crops and water conservation."
            else:
                return f"Near-normal rainfall expected for {location}. Standard agricultural practices recommended."

        elif "OND" in season:
            if phase == "El Nino":
                return f"Enhanced rainfall expected. High potential for flooding in {location}. Prepare drainage and emergency response."
            elif phase == "La Nina":
                return f"Suppressed rainfall expected. Poor short rains season likely for {location}."
            else:
                return f"Normal short rains expected for {location}."

        return f"Standard dry season conditions expected for {location}."

    async def _get_historical_comparison(self, location: str) -> Dict:
        """Get historical comparison data"""
        # This would typically query the database for historical data
        return {
            "last_5_years_average_rainfall_mm": 850,
            "last_year_rainfall_mm": 720,
            "deviation_from_average": -15.3,
            "trend": "decreasing"
        }

    async def get_anomalies(self, location: str, period: str) -> Dict:
        """Get climate anomalies for a location"""
        # Parse period
        period_days = {"1m": 30, "3m": 90, "6m": 180, "1y": 365, "5y": 1825}
        days = period_days.get(period, 365)

        return {
            "location": location,
            "period": period,
            "temperature_anomaly_c": 1.2,
            "rainfall_anomaly_percent": -15,
            "humidity_anomaly_percent": 5,
            "interpretation": "Temperatures above normal, rainfall below normal. Drought conditions developing.",
            "confidence": 0.72
        }
