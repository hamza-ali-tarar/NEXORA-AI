from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-create@nexora.ai",
            "full_name": "Users Create User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "users-create@nexora.ai"
    assert data["full_name"] == "Users Create User"
    assert "id" in data
    assert "created_at" in data


def test_duplicate_create_user(client: TestClient):
    payload = {
        "email": "users-duplicate@nexora.ai",
        "full_name": "First User",
    }

    first_response = client.post(
        "/api/v1/users/",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/users/",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_list_users(client: TestClient):
    client.post(
        "/api/v1/users/",
        json={
            "email": "users-list-one@nexora.ai",
            "full_name": "List User One",
        },
    )

    client.post(
        "/api/v1/users/",
        json={
            "email": "users-list-two@nexora.ai",
            "full_name": "List User Two",
        },
    )

    response = client.get("/api/v1/users/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["email"] == "users-list-one@nexora.ai"
    assert data[1]["email"] == "users-list-two@nexora.ai"


def test_get_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-get@nexora.ai",
            "full_name": "Get User",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/users/{user_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == "users-get@nexora.ai"
    assert data["full_name"] == "Get User"


def test_get_nonexistent_user(client: TestClient):
    response = client.get("/api/v1/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_update_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-update@nexora.ai",
            "full_name": "Before Update",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "email": "users-updated@nexora.ai",
            "full_name": "After Update",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == "users-updated@nexora.ai"
    assert data["full_name"] == "After Update"


def test_update_user_duplicate_email(client: TestClient):
    first_response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-update-first@nexora.ai",
            "full_name": "First User",
        },
    )

    second_response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-update-second@nexora.ai",
            "full_name": "Second User",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    second_user_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/users/{second_user_id}",
        json={
            "email": "users-update-first@nexora.ai",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "A user with this email already exists."
    )


def test_update_nonexistent_user(client: TestClient):
    response = client.patch(
        "/api/v1/users/999999",
        json={
            "full_name": "Updated User",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_delete_user(client: TestClient):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "users-delete@nexora.ai",
            "full_name": "Delete User",
        },
    )

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
    )

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/users/{user_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "User not found."