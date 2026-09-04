from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def test_root_endpoint(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "NEXORA AI"
    assert data["status"] == "online"
    assert data["version"] == "0.1.0"
    assert data["message"] == "NEXORA AI foundation is working."