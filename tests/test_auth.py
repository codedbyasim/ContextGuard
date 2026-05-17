import os
import sys
import importlib

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


@pytest.fixture
def authed_client():
    os.environ["AUTH_DISABLED"] = "false"
    import main

    importlib.reload(main)
    client = TestClient(main.app)
    reg = client.post(
        "/api/auth/register",
        json={
            "name": "Auth Tester",
            "email": "auth-tester@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    os.environ["AUTH_DISABLED"] = "true"
    importlib.reload(main)


def test_register_and_login():
    os.environ["AUTH_DISABLED"] = "false"
    import main

    importlib.reload(main)
    client = TestClient(main.app)

    email = "login-user@example.com"
    reg = client.post(
        "/api/auth/register",
        json={"name": "Login User", "email": email, "password": "password123"},
    )
    assert reg.status_code == 200
    assert reg.json()["user"]["email"] == email

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    os.environ["AUTH_DISABLED"] = "true"
    importlib.reload(main)


def test_protected_api_requires_token():
    os.environ["AUTH_DISABLED"] = "false"
    import main

    importlib.reload(main)
    client = TestClient(main.app)
    assert client.get("/api/status").status_code == 401
    os.environ["AUTH_DISABLED"] = "true"
    importlib.reload(main)


def test_authed_status(authed_client):
    res = authed_client.get("/api/status")
    assert res.status_code == 200
    assert "workspace" in res.json()
