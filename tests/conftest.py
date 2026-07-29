# # tests/conftest.py
# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool

# from app.main import app
# from app.core.database import Base, get_db
# from app.core.security import get_password_hash
# from app.models.user import User, UserRole

# # Test database
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @pytest.fixture(scope="function")
# def db_session():
#     Base.metadata.create_all(bind=engine)
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#         Base.metadata.drop_all(bind=engine)


# @pytest.fixture(scope="function")
# def client(db_session):
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass

#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as c:
#         yield c
#     app.dependency_overrides.clear()


# @pytest.fixture
# def auth_headers(client, db_session):
#     """Create a test user and return auth headers."""
#     user = User(
#         email="test@example.com",
#         username="testuser",
#         password_hash=get_password_hash("testpassword123"),
#         role=UserRole.ANALYST,
#     )
#     db_session.add(user)
#     db_session.commit()

#     response = client.post("/api/v1/auth/login", data={
#         "username": "test@example.com",
#         "password": "testpassword123",
#     })
#     token = response.json()["access_token"]
#     return {"Authorization": f"Bearer {token}"}


# @pytest.fixture
# def sample_csv(tmp_path):
#     """Create a sample CSV file for testing."""
#     import pandas as pd
#     import numpy as np

#     np.random.seed(42)
#     df = pd.DataFrame({
#         "feature_1": np.random.normal(100, 15, 200),
#         "feature_2": np.random.normal(50, 10, 200),
#         "feature_3": np.random.choice(["A", "B", "C"], 200),
#         "target": np.random.choice([0, 1], 200),
#     })
#     path = tmp_path / "test_data.csv"
#     df.to_csv(path, index=False)
#     return str(path)

import sys
import os
import pytest

# Add backend to Python path so 'app' module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return fake auth headers for testing."""
    return {"Authorization": "Bearer fake-test-token"}
