import pytest
from fastapi.testclient import TestClient

class TestPredictionRoutes:
    def test_predict_rainfall(self, client: TestClient):
        response = client.get("/api/predictions/rainfall/Nairobi?months=3")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert data["prediction_type"] == "rainfall"
        assert "monthly_breakdown" in data
        assert "confidence_score" in data

    def test_predict_drought(self, client: TestClient):
        response = client.get("/api/predictions/drought/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "drought_probability" in data
        assert "risk_level" in data

    def test_predict_flood(self, client: TestClient):
        response = client.get("/api/predictions/flood/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "flood_probability" in data
        assert "risk_level" in data

    def test_predict_temperature(self, client: TestClient):
        response = client.get("/api/predictions/temperature/Nairobi?months=3")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "monthly_breakdown" in data

    def test_get_comprehensive_prediction(self, client: TestClient):
        response = client.get("/api/predictions/comprehensive/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Nairobi"
        assert "predictions" in data
        assert "overall_risk_level" in data

    def test_trigger_retrain(self, client: TestClient):
        response = client.post("/api/predictions/retrain")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_get_model_performance(self, client: TestClient):
        response = client.get("/api/predictions/model-performance")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
