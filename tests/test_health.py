from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "NEXORA AI",
        "version": "v1",
    }


def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "pytest@nexora.ai",
            "full_name": "Pytest User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "pytest@nexora.ai"
    assert data["full_name"] == "Pytest User"
    assert "id" in data
    assert "created_at" in data


def test_duplicate_user_email(client: TestClient):
    email = "duplicate@nexora.ai"

    first_response = client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "full_name": "First User",
        },
    )

    second_response = client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "full_name": "Second User",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "A user with this email already exists."
    }


def test_get_users(client: TestClient):
    response = client.get("/api/v1/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_existing_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "getuser@nexora.ai",
            "full_name": "Get User",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == "getuser@nexora.ai"


def test_get_nonexistent_user(client: TestClient):
    response = client.get("/api/v1/users/999999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found."
    }


def test_update_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "update@nexora.ai",
            "full_name": "Original Name",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "full_name": "Updated Name",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == user_id
    assert data["email"] == "update@nexora.ai"
    assert data["full_name"] == "Updated Name"


def test_delete_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "delete@nexora.ai",
            "full_name": "Delete User",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/users/{user_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/api/v1/users/{user_id}"
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_user(client: TestClient):
    response = client.delete(
        "/api/v1/users/999999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found."
    }


def test_create_user_invalid_email(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "not-an-email",
            "full_name": "Invalid Email",
        },
    )

    assert response.status_code == 422


def test_create_user_missing_email(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Missing Email",
        },
    )

    assert response.status_code == 422


def test_update_user_invalid_email(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "validation@nexora.ai",
            "full_name": "Validation User",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "email": "invalid-email",
        },
    )

    assert update_response.status_code == 422