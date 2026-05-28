import pytest
from fastapi.testclient import TestClient

class TestWeatherRoutes:
    def test_get_current_weather(self, client: TestClient):
        response = client.get("/api/weather/current/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "current" in data
        assert "coordinates" in data

    def test_get_current_weather_invalid_location(self, client: TestClient):
        response = client.get("/api/weather/current/InvalidLocation")
        assert response.status_code == 404

    def test_get_weather_forecast(self, client: TestClient):
        response = client.get("/api/weather/forecast/Nairobi?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "daily" in data
        assert data["forecast_days"] == 7

    def test_get_weather_forecast_default_days(self, client: TestClient):
        response = client.get("/api/weather/forecast/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["forecast_days"] == 7

    def test_get_historical_weather(self, client: TestClient):
        response = client.get(
            "/api/weather/historical/Nairobi?start_date=2024-01-01&end_date=2024-01-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "data" in data

    def test_get_historical_weather_missing_params(self, client: TestClient):
        response = client.get("/api/weather/historical/Nairobi")
        assert response.status_code == 422
