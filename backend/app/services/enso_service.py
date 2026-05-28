import httpx
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ENSOService:
    """Service for fetching and analyzing El Nino/La Nina data"""

    NOAA_ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    NOAA_SOI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/soi"

    def __init__(self):
        self._cache = {}

    def _classify_enso(self, oni: float) -> str:
        """Classify ENSO phase based on ONI value"""
        if oni >= 0.5:
            return "El Nino"
        elif oni <= -0.5:
            return "La Nina"
        return "Neutral"

    def _get_severity(self, oni: float) -> str:
        """Get ENSO severity"""
        abs_oni = abs(oni)
        if abs_oni >= 2.0:
            return "Strong"
        elif abs_oni >= 1.5:
            return "Moderate"
        elif abs_oni >= 1.0:
            return "Weak"
        return "Very Weak"

    async def get_current_status(self) -> Dict:
        """Get current ENSO status"""
        try:
            # Fetch latest ONI data from NOAA
            async with httpx.AsyncClient() as client:
                response = await client.get(self.NOAA_ONI_URL, timeout=30.0)

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                # Parse the last line for latest data
                data_lines = [l for l in lines if l.strip() and not l.startswith(' ') and len(l.split()) >= 3]

                if data_lines:
                    latest = data_lines[-1].split()
                    year = int(latest[0])
                    month = latest[1]
                    oni = float(latest[2])

                    phase = self._classify_enso(oni)
                    severity = self._get_severity(oni)

                    return {
                        "status": "success",
                        "current_phase": phase,
                        "severity": severity,
                        "oni_value": round(oni, 2),
                        "period": f"{month} {year}",
                        "year": year,
                        "month": month,
                        "description": self._get_phase_description(phase, severity, oni),
                        "typical_duration_months": self._get_typical_duration(phase),
                        "last_updated": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error fetching ENSO data: {e}")

        # Fallback: return simulated current status based on typical patterns
        return self._get_simulated_status()

    def _get_simulated_status(self) -> Dict:
        """Generate simulated ENSO status when API is unavailable"""
        # Based on 2024-2025 La Nina conditions
        return {
            "status": "simulated",
            "current_phase": "La Nina",
            "severity": "Weak",
            "oni_value": -0.8,
            "period": "Recent 3-month average",
            "description": "Weak La Nina conditions are present. Cooler than average sea surface temperatures in the central and eastern tropical Pacific.",
            "typical_duration_months": 9,
            "last_updated": datetime.utcnow().isoformat(),
            "note": "Using simulated data - NOAA API may be temporarily unavailable"
        }

    def _get_phase_description(self, phase: str, severity: str, oni: float) -> str:
        """Get human-readable phase description"""
        descriptions = {
            "El Nino": f"{severity} El Nino conditions present. Warmer than average sea surface temperatures in the central and eastern tropical Pacific (ONI: {oni}). Typically brings wetter conditions to East Africa during OND season.",
            "La Nina": f"{severity} La Nina conditions present. Cooler than average sea surface temperatures in the central and eastern tropical Pacific (ONI: {oni}). Often associated with drought conditions in East Africa.",
            "Neutral": f"ENSO-neutral conditions. Sea surface temperatures near average in the tropical Pacific (ONI: {oni}). No strong El Nino or La Nina influence expected."
        }
        return descriptions.get(phase, "Unknown ENSO phase")

    def _get_typical_duration(self, phase: str) -> int:
        """Get typical duration in months"""
        durations = {"El Nino": 9, "La Nina": 12, "Neutral": 6}
        return durations.get(phase, 6)

    async def get_historical_data(self, years: int = 10, include_forecast: bool = True) -> Dict:
        """Get historical ENSO data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.NOAA_ONI_URL, timeout=30.0)

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []

                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        year = int(parts[0])
                        month = parts[1]
                        oni = float(parts[2])

                        if datetime.now().year - year <= years:
                            data.append({
                                "year": year,
                                "month": month,
                                "oni": oni,
                                "phase": self._classify_enso(oni),
                                "severity": self._get_severity(oni)
                            })

                return {
                    "period_years": years,
                    "total_records": len(data),
                    "data": data,
                    "phase_distribution": self._calculate_phase_distribution(data),
                    "last_updated": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching historical ENSO data: {e}")

        return self._get_simulated_historical(years)

    def _calculate_phase_distribution(self, data: List[Dict]) -> Dict:
        """Calculate distribution of ENSO phases"""
        from collections import Counter
        phases = [d["phase"] for d in data]
        return dict(Counter(phases))

    def _get_simulated_historical(self, years: int) -> Dict:
        """Generate simulated historical data"""
        import random
        data = []
        current_year = datetime.now().year

        for y in range(current_year - years, current_year + 1):
            for m in ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]:
                # Simulate realistic ONI patterns
                oni = random.gauss(0, 0.8)
                oni = max(-2.5, min(2.5, oni))

                data.append({
                    "year": y,
                    "month": m,
                    "oni": round(oni, 2),
                    "phase": self._classify_enso(oni),
                    "severity": self._get_severity(oni)
                })

        return {
            "period_years": years,
            "total_records": len(data),
            "data": data[-(years*12):],
            "phase_distribution": self._calculate_phase_distribution(data),
            "note": "Simulated historical data",
            "last_updated": datetime.utcnow().isoformat()
        }
