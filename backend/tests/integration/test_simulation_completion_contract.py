import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ANTHROPIC_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.db.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.simulation import Simulation  # noqa: E402
from app.models.video import Video  # noqa: E402
from app.services.simulation_service import execute_simulation  # noqa: E402


client = TestClient(app)


def test_completed_simulation_always_has_report():
    email = f"contract-{uuid.uuid4()}@example.com"
    password = "password123"
    register = client.post(
        "/api/auth/register",
        json={"name": "Contract User", "email": email, "password": password},
    )
    user_id = register.json()["id"]
    token = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    ).json()["access_token"]

    db = SessionLocal()
    try:
        video = Video(
            user_id=user_id,
            title="Demo",
            filename="demo.mp4",
            file_path="unused.mp4",
            file_size=12,
            status="uploaded",
        )
        db.add(video)
        db.flush()
        simulation = Simulation(
            video_id=video.id,
            user_id=user_id,
            target_audience="solo founders testing product demos",
            persona_count=50,
            round_count=3,
            status="queued",
            progress_stage="queued",
        )
        db.add(simulation)
        db.commit()
        simulation_id = simulation.id

        execute_simulation(db, simulation_id)
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    simulation_response = client.get(f"/api/simulations/{simulation_id}", headers=headers)
    assert simulation_response.status_code == 200
    simulation_payload = simulation_response.json()
    assert simulation_payload["status"] == "completed"
    assert simulation_payload["transcript_ai_source"] == "fallback"
    assert simulation_payload["content_analysis_ai_source"] == "fallback"
    assert simulation_payload["personas_ai_source"] == "fallback"
    assert simulation_payload["reasons_ai_source"] == "fallback"

    report_response = client.get(f"/api/simulations/{simulation_id}/report", headers=headers)
    assert report_response.status_code == 200
    assert report_response.json()["summary"]

    graph_response = client.get(f"/api/simulations/{simulation_id}/graph", headers=headers)
    assert graph_response.status_code == 200
    assert graph_response.json()["nodes"]

    rounds_response = client.get(f"/api/simulations/{simulation_id}/rounds", headers=headers)
    assert rounds_response.status_code == 200
    assert rounds_response.json()


def test_report_creation_failure_marks_simulation_failed(monkeypatch):
    email = f"report-failure-{uuid.uuid4()}@example.com"
    password = "password123"
    register = client.post(
        "/api/auth/register",
        json={"name": "Report Failure User", "email": email, "password": password},
    )
    user_id = register.json()["id"]

    def fail_report(*args, **kwargs):
        raise RuntimeError("synthetic report failure")

    monkeypatch.setattr("app.services.simulation_service.create_report", fail_report)

    db = SessionLocal()
    try:
        video = Video(
            user_id=user_id,
            title="Demo",
            filename="demo.mp4",
            file_path="unused.mp4",
            file_size=12,
            status="uploaded",
        )
        db.add(video)
        db.flush()
        simulation = Simulation(
            video_id=video.id,
            user_id=user_id,
            target_audience="solo founders testing product demos",
            persona_count=50,
            round_count=3,
            status="queued",
            progress_stage="queued",
        )
        db.add(simulation)
        db.commit()
        simulation_id = simulation.id

        result = execute_simulation(db, simulation_id)
    finally:
        db.close()

    assert result.status == "failed"
    assert result.progress_stage == "failed"
    assert "Report creation failed" in result.error_message
