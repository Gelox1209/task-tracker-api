"""Tests follow the Arrange -> Act -> Assert pattern."""


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Learn Git", "description": "branches + PRs"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Learn Git"
    assert data["done"] is False


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422  # validation error


def test_create_task_requires_title(client):
    response = client.post("/tasks", json={"description": "no title"})
    assert response.status_code == 422


def test_list_tasks(client):
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})

    response = client.get("/tasks")

    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["First", "Second"]


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_task(client):
    created = client.post("/tasks", json={"title": "Write tests"}).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Write tests"


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
