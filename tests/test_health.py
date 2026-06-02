from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "marketing-parser"}


def test_readiness() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "marketing-parser"}
