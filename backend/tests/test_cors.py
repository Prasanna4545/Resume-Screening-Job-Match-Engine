from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_headers_allowed_origin():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    print("\nCORS OPTIONS response headers for http://localhost:5173:")
    print("Access-Control-Allow-Origin:", response.headers.get("access-control-allow-origin"))
    print("Access-Control-Allow-Methods:", response.headers.get("access-control-allow-methods"))

def test_cors_disallowed_origin():
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://unauthorized-domain.com",
            "Access-Control-Request-Method": "GET",
        }
    )
    # FastApi/Starlette CORS middleware does not return Access-Control-Allow-Origin for unauthorized origins
    assert response.headers.get("access-control-allow-origin") != "http://unauthorized-domain.com"
    print("\nCORS OPTIONS response headers for unauthorized domain:")
    print("Access-Control-Allow-Origin:", response.headers.get("access-control-allow-origin"))
