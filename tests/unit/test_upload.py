# tests/unit/test_upload.py
import pytest
from fastapi.testclient import TestClient
import io


class TestUpload:
    def test_upload_csv(self, client, auth_headers):
        """Test CSV file upload."""
        csv_content = "col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n"
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.csv"
        assert data["file_type"] == "csv"
        assert data["row_count"] == 3

    def test_upload_invalid_type(self, client, auth_headers):
        """Test upload with invalid file type."""
        files = {"file": ("test.exe", io.BytesIO(b"invalid"), "application/octet-stream")}
        response = client.post(
            "/api/v1/upload/",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_upload_unauthorized(self, client):
        """Test upload without authentication."""
        files = {"file": ("test.csv", io.BytesIO(b"a,b\n1,2"), "text/csv")}
        response = client.post("/api/v1/upload/", files=files)
        assert response.status_code == 401

    def test_list_datasets(self, client, auth_headers):
        """Test listing datasets."""
        response = client.get("/api/v1/upload/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
