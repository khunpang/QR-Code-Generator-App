from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

def test_login_for_access_token():
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
