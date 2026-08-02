import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    print("\nGET /api/health response:", data)
    assert data["status"] == "ok"

def test_db_health_endpoint():
    response = client.get("/api/db-health")
    assert response.status_code == 200
    data = response.json()
    print("\nGET /api/db-health response:", data)
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["result"] == 1
