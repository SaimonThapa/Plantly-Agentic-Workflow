from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_api_contract():
    with TestClient(create_app()) as client:
        for path in ("/health", "/api/v1/health"):
            response = client.get(path)
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
        assert "/api/v1/health" in client.get("/openapi.json").json()["paths"]
