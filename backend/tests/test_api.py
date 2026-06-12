import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_invalid_extension():
    data = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = client.post("/api/v1/analyze", files=data)
    assert response.status_code == 400


def test_analyze_no_file():
    response = client.post("/api/v1/analyze")
    assert response.status_code == 422


def test_ai_analyze_invalid_extension():
    data = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = client.post("/api/v1/ai/analyze", files=data)
    assert response.status_code == 400


def test_ai_summary_invalid_extension():
    data = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = client.post("/api/v1/ai/summary", files=data)
    assert response.status_code == 400
