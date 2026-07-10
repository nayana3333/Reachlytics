import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ANTHROPIC_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


client = TestClient(app)


def test_register_and_login_flow():
    email = f"user-{uuid.uuid4()}@example.com"
    payload = {"name": "Placement User", "email": email, "password": "password123"}

    register_response = client.post("/api/auth/register", json=payload)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == email

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_me_requires_authentication():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
