import pytest
from fastapi.testclient import TestClient

class TestClimateRoutes:
    def test_get_current_enso(self, client: TestClient):
        response = client.get("/api/climate/enso/current")
        assert response.status_code == 200
        data = response.json()
        assert "current_phase" in data
        assert "oni_value" in data
        assert "severity" in data

    def test_get_enso_history(self, client: TestClient):
        response = client.get("/api/climate/enso/history?years=5")
        assert response.status_code == 200
        data = response.json()
        assert "period_years" in data
        assert "data" in data

    def test_get_enso_impact(self, client: TestClient):
        response = client.get("/api/climate/enso/impact/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "enso_status" in data
        assert "risk_assessment" in data

    def test_get_enso_impact_invalid_location(self, client: TestClient):
        response = client.get("/api/climate/enso/impact/InvalidLocation")
        assert response.status_code == 404

    def test_get_seasonal_outlook(self, client: TestClient):
        response = client.get("/api/climate/seasonal/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "current_season" in data
        assert "outlook" in data

    def test_get_climate_anomalies(self, client: TestClient):
        response = client.get("/api/climate/anomalies/Nairobi?period=1y")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "temperature_anomaly_c" in data
