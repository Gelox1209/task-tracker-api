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


def test_update_task_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Old title"}).json()

    # Update the task
    response = client.patch(f"/tasks/{created['id']}", json={"title": "New title"})

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["done"] is False  # default value


def test_update_missing_task_returns_404(client):
    response = client.patch("/tasks/999", json={"title": "Doesn't matter"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_description(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Partial update", "description": "Initial description"}).json()

    # Update only the description
    response = client.patch(f"/tasks/{created['id']}", json={"description": "Updated description"})

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Partial update"  # title should remain unchanged
    assert data["description"] == "Updated description"
    assert data["done"] is False  # default value


def test_update_task_no_changes(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "No changes", "description": "Initial description"}).json()

    # Update with no changes
    response = client.patch(f"/tasks/{created['id']}", json={})

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "No changes"
    assert data["description"] == "Initial description"
    assert data["done"] is False  # default value


def test_update_full_update(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Full update", "description": "Initial description"}).json()

    # Update both title and description
    response = client.patch(f"/tasks/{created['id']}", json={"title": "Updated title", "description": "Updated description", "done": True})

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated description"
    assert data["done"] is True


def test_update_task_done_status(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Update done status"}).json()

    # Update the done status
    response = client.patch(f"/tasks/{created['id']}", json={"done": True})

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Update done status"
    assert data["done"] is True


def test_update_blank_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Original title"}).json()

    # Update with a blank title
    response = client.patch(f"/tasks/{created['id']}", json={"title": ""})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_null_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Original title"}).json()

    # Update with a null title
    response = client.patch(f"/tasks/{created['id']}", json={"title": None})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_null_done(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Original title"}).json()

    # Update with a null done status
    response = client.patch(f"/tasks/{created['id']}", json={"done": None})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_null_description(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Original title", "description": "Original description"}).json()

    # Update with a null description
    response = client.patch(f"/tasks/{created['id']}", json={"description": None})

    # Assert the response
    assert response.status_code == 200  # Should be valid to set description to None
    data = response.json()
    assert data["description"] is None


def test_delete_task(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task to delete"}).json()

    # Delete the task
    response = client.delete(f"/tasks/{created['id']}")

    # Assert the response
    assert response.status_code == 204

    # Verify the task is actually deleted
    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"