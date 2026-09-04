from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-register@nexora.ai",
            "password": "TestPassword123!",
            "full_name": "Auth Register User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "auth-register@nexora.ai"
    assert data["full_name"] == "Auth Register User"
    assert "id" in data
    assert "created_at" in data


def test_duplicate_register_email(client: TestClient):
    payload = {
        "email": "auth-duplicate@nexora.ai",
        "password": "TestPassword123!",
        "full_name": "First User",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json={
            **payload,
            "full_name": "Second User",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_user(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-login@nexora.ai",
            "password": "TestPassword123!",
            "full_name": "Auth Login User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "auth-login@nexora.ai",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert data["access_token"]


def test_login_wrong_password(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-wrong@nexora.ai",
            "password": "TestPassword123!",
            "full_name": "Wrong Password User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "auth-wrong@nexora.ai",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_me_requires_authentication(client: TestClient):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_valid_token(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-me@nexora.ai",
            "password": "TestPassword123!",
            "full_name": "Auth Me User",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "auth-me@nexora.ai",
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "auth-me@nexora.ai"
    assert data["full_name"] == "Auth Me User"