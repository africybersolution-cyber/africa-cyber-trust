"""Test auth endpoint directly."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test signup
response = client.post(
    "/api/auth/signup",
    json={"email": "test@test.com", "password": "Test1234!", "name": "Test"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
