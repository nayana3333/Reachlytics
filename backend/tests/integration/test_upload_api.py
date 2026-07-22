import io
import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _token() -> str:
    email = f"upload-{uuid.uuid4()}@example.com"
    password = "password123"
    client.post(
        "/api/auth/register",
        json={"name": "Upload User", "email": email, "password": password},
    )
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def test_upload_rejects_non_video_extension():
    response = client.post(
        "/api/videos/upload",
        headers={"Authorization": f"Bearer {_token()}"},
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported video type" in response.json()["detail"]


def test_upload_accepts_video_file_metadata():
    response = client.post(
        "/api/videos/upload",
        headers={"Authorization": f"Bearer {_token()}"},
        files={"file": ("demo.mp4", io.BytesIO(b"not-a-real-video-but-valid-upload"), "video/mp4")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "demo.mp4"
    assert body["status"] == "uploaded"
