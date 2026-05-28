import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_enso_data():
    return {
        "current_phase": "La Nina",
        "severity": "Weak",
        "oni_value": -0.8,
        "period": "Recent 3-month average",
        "description": "Weak La Nina conditions present",
        "typical_duration_months": 9,
        "last_updated": "2024-05-26T12:00:00"
    }

@pytest.fixture
def mock_weather_data():
    return {
        "location": "Nairobi",
        "coordinates": {"lat": -1.2921, "lon": 36.8219},
        "elevation": 1795,
        "region": "Central Highlands",
        "current": {
            "temperature_2m": 24.5,
            "relative_humidity_2m": 65,
            "precipitation": 0.0,
            "weather_code": 1,
            "wind_speed_10m": 12,
            "wind_direction_10m": 180,
            "pressure_msl": 1015,
            "cloud_cover": 25
        },
        "timestamp": "2024-05-26T12:00:00"
    }

@pytest.fixture
def mock_prediction_data():
    return {
        "location": "Nairobi",
        "prediction_type": "rainfall",
        "period_months": 3,
        "total_predicted_mm": 150.5,
        "monthly_breakdown": [
            {"month": 6, "predicted_mm": 45.2, "confidence": 0.72},
            {"month": 7, "predicted_mm": 55.8, "confidence": 0.68},
            {"month": 8, "predicted_mm": 49.5, "confidence": 0.75}
        ],
        "enso_influence": {
            "phase": "La Nina",
            "oni": -0.8,
            "adjustment_mm": -25.3
        },
        "confidence_score": 0.72,
        "model_version": "1.0.0",
        "timestamp": "2024-05-26T12:00:00"
    }
