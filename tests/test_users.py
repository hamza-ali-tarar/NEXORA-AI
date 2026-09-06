from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient,
    email: str,
    password: str = "password123",
    full_name: str = "Test User",
):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
    }


def test_users_require_authentication(client: TestClient):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_get_my_user(client: TestClient):
    token = register_and_login(
        client,
        "users-me@nexora.ai",
        full_name="My User",
    )

    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "users-me@nexora.ai"
    assert data["full_name"] == "My User"
    assert "id" in data
    assert "created_at" in data


def test_update_my_user(client: TestClient):
    token = register_and_login(
        client,
        "users-update@nexora.ai",
        full_name="Before Update",
    )

    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={
            "email": "users-updated@nexora.ai",
            "full_name": "After Update",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "users-updated@nexora.ai"
    assert data["full_name"] == "After Update"


def test_update_my_user_duplicate_email(client: TestClient):
    register_and_login(
        client,
        "users-update-first@nexora.ai",
        full_name="First User",
    )

    second_token = register_and_login(
        client,
        "users-update-second@nexora.ai",
        full_name="Second User",
    )

    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers(second_token),
        json={
            "email": "users-update-first@nexora.ai",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A user with this email already exists."
    )


def test_delete_my_user(client: TestClient):
    token = register_and_login(
        client,
        "users-delete@nexora.ai",
        full_name="Delete User",
    )

    delete_response = client.delete(
        "/api/v1/users/me",
        headers=auth_headers(token),
    )

    assert delete_response.status_code == 204

    me_response = client.get(
        "/api/v1/users/me",
        headers=auth_headers(token),
    )

    assert me_response.status_code == 401