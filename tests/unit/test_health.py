import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_returns_version(self):
        response = client.get("/health")
        data = response.json()
        assert "version" in data

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_message(self):
        response = client.get("/")
        data = response.json()
        assert "message" in data
