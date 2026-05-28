import pytest
from fastapi.testclient import TestClient

class TestLocationRoutes:
    def test_search_locations(self, client: TestClient):
        response = client.get("/api/locations/search?q=Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert len(data["results"]) > 0

    def test_search_locations_empty_query(self, client: TestClient):
        response = client.get("/api/locations/search?q=a")
        assert response.status_code == 422

    def test_get_all_locations(self, client: TestClient):
        response = client.get("/api/locations/all")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert len(data["locations"]) > 0

    def test_get_all_locations_by_region(self, client: TestClient):
        response = client.get("/api/locations/all?region=Coastal")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data

    def test_get_regions(self, client: TestClient):
        response = client.get("/api/locations/regions")
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert len(data["regions"]) > 0

    def test_get_location_details(self, client: TestClient):
        response = client.get("/api/locations/Nairobi")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nairobi"
        assert "climate_profile" in data
        assert "rainy_seasons" in data

    def test_get_location_details_invalid(self, client: TestClient):
        response = client.get("/api/locations/InvalidLocation")
        assert response.status_code == 404
