import pytest
from fastapi.testclient import TestClient

class TestMainApp:
    def test_root_endpoint(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kenyan Climate & Weather Prediction API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data

    def test_enso_status_endpoint(self, client: TestClient):
        response = client.get("/api/ensostatus")
        assert response.status_code == 200
        data = response.json()
        assert "current_phase" in data
        assert "oni_value" in data

    def test_api_docs(self, client: TestClient):
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_redoc(self, client: TestClient):
        response = client.get("/api/redoc")
        assert response.status_code == 200
