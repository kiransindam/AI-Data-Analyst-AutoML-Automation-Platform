import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIEndpoints:
    def test_docs_available(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "AI AutoML Platform"

    def test_404_for_unknown_route(self):
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
