from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str) -> str:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Knowledge User",
        },
    )

    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert login.status_code == 200

    return login.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_create_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge1@nexora.ai")

    response = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Python Basics",
            "content": "Python is a programming language.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Basics"
    assert data["content"] == "Python is a programming language."
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_list_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge2@nexora.ai")

    client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "First",
            "content": "First document.",
        },
    )

    client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Second",
            "content": "Second document.",
        },
    )

    response = client.get(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "First"
    assert data[1]["title"] == "Second"


def test_get_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge3@nexora.ai")

    create = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "My Document",
            "content": "Document content.",
        },
    )

    assert create.status_code == 201

    document_id = create.json()["id"]

    response = client.get(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["title"] == "My Document"


def test_update_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge5@nexora.ai")

    create = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Original Title",
            "content": "Original content.",
        },
    )

    assert create.status_code == 201

    document_id = create.json()["id"]

    update = client.patch(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(token),
        json={
            "title": "Updated Title",
            "content": "Updated content.",
        },
    )

    assert update.status_code == 200

    data = update.json()

    assert data["id"] == document_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content."


def test_user_cannot_update_other_users_document(client: TestClient):
    owner_token = register_and_login(
        client,
        "knowledge-update-owner@nexora.ai",
    )

    create = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(owner_token),
        json={
            "title": "Private",
            "content": "Private document.",
        },
    )

    assert create.status_code == 201

    document_id = create.json()["id"]

    other_token = register_and_login(
        client,
        "knowledge-update-other@nexora.ai",
    )

    response = client.patch(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(other_token),
        json={
            "title": "Hacked",
            "content": "This should not be allowed.",
        },
    )

    assert response.status_code == 404


def test_delete_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge4@nexora.ai")

    create = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Delete Me",
            "content": "Delete this document.",
        },
    )

    assert create.status_code == 201

    document_id = create.json()["id"]

    delete = client.delete(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(token),
    )

    assert delete.status_code == 204

    get_response = client.get(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_knowledge_requires_authentication(client: TestClient):
    response = client.get("/api/v1/knowledge/")

    assert response.status_code == 401


def test_user_cannot_access_other_users_document(client: TestClient):
    owner_token = register_and_login(
        client,
        "knowledge-owner@nexora.ai",
    )

    create = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(owner_token),
        json={
            "title": "Private",
            "content": "Private document.",
        },
    )

    assert create.status_code == 201

    document_id = create.json()["id"]

    other_token = register_and_login(
        client,
        "knowledge-other@nexora.ai",
    )

    response = client.get(
        f"/api/v1/knowledge/{document_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 404


def test_search_knowledge(client: TestClient):
    token = register_and_login(client, "knowledge-search@nexora.ai")

    client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "Python Guide",
            "content": "Learn Python programming.",
        },
    )

    client.post(
        "/api/v1/knowledge/",
        headers=auth_headers(token),
        json={
            "title": "FastAPI Guide",
            "content": "Build APIs with FastAPI.",
        },
    )

    response = client.get(
        "/api/v1/knowledge/?search=python",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Python Guide"


def test_knowledge_pagination_limit(client: TestClient):
    token = register_and_login(client, "knowledge-limit@nexora.ai")

    for index in range(3):
        response = client.post(
            "/api/v1/knowledge/",
            headers=auth_headers(token),
            json={
                "title": f"Document {index + 1}",
                "content": f"Content {index + 1}",
            },
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/knowledge/?limit=2",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Document 1"
    assert data[1]["title"] == "Document 2"


def test_knowledge_pagination_skip(client: TestClient):
    token = register_and_login(client, "knowledge-skip@nexora.ai")

    for index in range(3):
        response = client.post(
            "/api/v1/knowledge/",
            headers=auth_headers(token),
            json={
                "title": f"Document {index + 1}",
                "content": f"Content {index + 1}",
            },
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/knowledge/?skip=1&limit=2",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Document 2"
    assert data[1]["title"] == "Document 3"