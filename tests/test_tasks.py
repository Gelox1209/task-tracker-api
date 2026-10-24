"""Tests follow the Arrange -> Act -> Assert pattern."""


def task_create_many(client, count):
    """Helper function to create many tasks."""
    for i in range(count):
        client.post("/tasks", json={"title": f"Task {i + 1}"})


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post(
        "/tasks", json={"title": "Learn Git", "description": "branches + PRs"}
    )

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


def test_create_task_rejects_long_title(client):
    long_title = "a" * 201  # 201 characters
    response = client.post("/tasks", json={"title": long_title})
    assert response.status_code == 422


def test_create_strip_whitespace_title(client):
    response = client.post("/tasks", json={"title": "   Trim me   "})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Trim me"  # whitespace should be stripped


def test_create_task_accepts_200_char_title(client):
    max_length_title = "a" * 200  # 200 characters
    response = client.post("/tasks", json={"title": max_length_title})
    assert response.status_code == 201  # success


def test_create_task_accepts_1_char_title(client):
    min_length_title = "a"  # 1 character
    response = client.post("/tasks", json={"title": min_length_title})
    assert response.status_code == 201  # success


def test_create_task_already_done(client):
    response = client.post("/tasks", json={"title": "Already done", "done": True})
    assert response.status_code == 201
    data = response.json()
    assert data["done"] is True


def test_create_task_rejects_whitespace_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_rejects_null_title(client):
    response = client.post("/tasks", json={"title": None})
    assert response.status_code == 422  # validation error


def test_create_task_rejects_null_done(client):
    response = client.post(
        "/tasks", json={"title": "Task with null done", "done": None}
    )
    assert response.status_code == 422  # validation error


def test_create_task_accepts_null_description(client):
    response = client.post(
        "/tasks", json={"title": "Task with null description", "description": None}
    )
    assert response.status_code == 201  # success


def test_create_task_rejects_long_description(client):
    long_description = "a" * 1001  # 1001 characters
    response = client.post(
        "/tasks",
        json={"title": "Task with long description", "description": long_description},
    )
    assert response.status_code == 422  # validation error


def test_create_task_accepts_1000_char_description(client):
    long_description = "a" * 1000  # 1000 characters
    response = client.post(
        "/tasks",
        json={
            "title": "Task with max length description",
            "description": long_description,
        },
    )
    assert response.status_code == 201  # success


def test_create_task_accepts_1_char_description(client):
    short_description = "a"  # 1 character
    response = client.post(
        "/tasks",
        json={
            "title": "Task with min length description",
            "description": short_description,
        },
    )
    assert response.status_code == 201  # success


def test_create_task_accepts_empty_description(client):
    response = client.post(
        "/tasks", json={"title": "Task with empty description", "description": ""}
    )
    assert response.status_code == 201  # success


def test_create_task_accepts_whitespace_description(client):
    response = client.post(
        "/tasks",
        json={"title": "Task with whitespace description", "description": "   "},
    )
    assert response.status_code == 201  # success


def test_create_task_accepts_missing_description(client):
    response = client.post("/tasks", json={"title": "Task with missing description"})
    assert response.status_code == 201  # success


def test_create_task_rejects_extra_fields(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Task with extra fields",
            "description": "This should fail",
            "extra_field": "not allowed",
        },
    )
    assert response.status_code == 422  # validation error


def test_list_tasks(client):
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})

    response = client.get("/tasks")

    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["First", "Second"]


def test_check_default_limit_and_offset(client):
    # Create 15 tasks
    task_create_many(client, 15)

    # Test default limit=10 and offset=0 (should return Task 1 to Task 10)
    response = client.get("/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == [f"Task {i + 1}" for i in range(10)]


def test_list_tasks_with_limit_and_offset(client):
    # Create 5 tasks
    task_create_many(client, 5)

    # Test limit=2, offset=1 (should return Task 2 and Task 3)
    response = client.get("/tasks?limit=2&offset=1")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 2", "Task 3"]


def test_list_tasks_with_limit_only(client):
    # Create 5 tasks
    task_create_many(client, 5)

    # Test limit=3 (should return Task 1, Task 2, Task 3)
    response = client.get("/tasks?limit=3")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 1", "Task 2", "Task 3"]


def test_list_tasks_with_offset_only(client):
    # Create 5 tasks
    task_create_many(client, 5)

    # Test offset=2 (should return Task 3, Task 4, Task 5)
    response = client.get("/tasks?offset=2")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 3", "Task 4", "Task 5"]


def test_list_tasks_with_invalid_limit(client):
    response = client.get("/tasks?limit=0")
    assert response.status_code == 422

    response = client.get("/tasks?limit=101")
    assert response.status_code == 422


def test_list_tasks_with_100_limit(client):
    # Create 150 tasks
    task_create_many(client, 150)

    # Test limit=100 (should return Task 1 to Task 100)
    response = client.get("/tasks?limit=100")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == [f"Task {i + 1}" for i in range(100)]


def test_list_tasks_with_1_limit(client):
    # Create 5 tasks
    task_create_many(client, 5)

    # Test limit=1 (should return Task 1)
    response = client.get("/tasks?limit=1")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 1"]


def test_list_tasks_with_invalid_offset(client):
    response = client.get("/tasks?offset=-1")
    assert response.status_code == 422


def test_list_tasks_with_done_filter(client):
    # Create tasks with different done statuses
    client.post("/tasks", json={"title": "Task 1", "done": False})
    client.post("/tasks", json={"title": "Task 2", "done": True})
    client.post("/tasks", json={"title": "Task 3", "done": False})

    # Test filtering for done=True
    response = client.get("/tasks?done=true")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 2"]

    # Test filtering for done=False
    response = client.get("/tasks?done=false")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 1", "Task 3"]


def test_list_tasks_with_invalid_done_filter(client):
    response = client.get("/tasks?done=notabool")
    assert response.status_code == 422  # FastAPI will reject invalid boolean values


def test_list_tasks_with_done_filter_and_pagination(client):
    # Create tasks with different done statuses
    client.post("/tasks", json={"title": "Task 1", "done": False})
    client.post("/tasks", json={"title": "Task 2", "done": True})
    client.post("/tasks", json={"title": "Task 3", "done": False})
    client.post("/tasks", json={"title": "Task 4", "done": True})
    client.post("/tasks", json={"title": "Task 5", "done": False})

    # Test filtering for done=False with limit=2 and offset=1
    response = client.get("/tasks?done=false&limit=2&offset=1")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 3", "Task 5"]


def test_list_tasks_with_unknown_field(client):
    # Test filtering with an unknown query parameter
    response = client.get("/tasks?unknown_field=value")
    assert response.status_code == 422  # FastAPI will reject unknown query parameters


def test_list_tasks_with_done_filter_no_results(client):
    # Create tasks with different done statuses
    client.post("/tasks", json={"title": "Task 1", "done": False})
    client.post("/tasks", json={"title": "Task 2", "done": True})

    # Test filtering for done=True with limit=1 and offset=1 (should return no results)
    response = client.get("/tasks?done=true&limit=1&offset=1")
    assert response.status_code == 200
    assert response.json() == []  # No tasks should be returned


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


def test_update_task_with_unknown_field(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with unknown field"}).json()

    # Attempt to update with an unknown field
    response = client.patch(
        f"/tasks/{created['id']}", json={"unknown_field": "some value"}
    )

    # Assert the response
    assert response.status_code == 422  # FastAPI will reject unknown fields


def test_update_task_with_empty_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with empty title"}).json()

    # Attempt to update with an empty title
    response = client.patch(f"/tasks/{created['id']}", json={"title": ""})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_task_with_whitespace_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with whitespace title"}).json()

    # Attempt to update with a whitespace title
    response = client.patch(f"/tasks/{created['id']}", json={"title": "   "})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_task_with_long_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with long title"}).json()

    # Attempt to update with a title that exceeds the maximum length
    long_title = "a" * 201  # 201 characters
    response = client.patch(f"/tasks/{created['id']}", json={"title": long_title})

    # Assert the response
    assert response.status_code == 422  # Unprocessable Entity


def test_update_task_with_200_char_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with 200 char title"}).json()

    # Attempt to update with a title that is exactly the maximum length
    max_length_title = "a" * 200  # 200 characters
    response = client.patch(f"/tasks/{created['id']}", json={"title": max_length_title})

    # Assert the response
    assert response.status_code == 200  # Should be valid
    data = response.json()
    assert data["title"] == max_length_title


def test_update_task_with_1_char_title(client):
    # Create a task first
    created = client.post("/tasks", json={"title": "Task with 1 char title"}).json()

    # Attempt to update with a title that is exactly the minimum length
    min_length_title = "a"  # 1 character
    response = client.patch(f"/tasks/{created['id']}", json={"title": min_length_title})

    # Assert the response
    assert response.status_code == 200  # Should be valid
    data = response.json()
    assert data["title"] == min_length_title


def test_update_missing_task_returns_404(client):
    response = client.patch("/tasks/999", json={"title": "Doesn't matter"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_description(client):
    # Create a task first
    created = client.post(
        "/tasks", json={"title": "Partial update", "description": "Initial description"}
    ).json()

    # Update only the description
    response = client.patch(
        f"/tasks/{created['id']}", json={"description": "Updated description"}
    )

    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Partial update"  # title should remain unchanged
    assert data["description"] == "Updated description"
    assert data["done"] is False  # default value


def test_update_task_no_changes(client):
    # Create a task first
    created = client.post(
        "/tasks", json={"title": "No changes", "description": "Initial description"}
    ).json()

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
    created = client.post(
        "/tasks", json={"title": "Full update", "description": "Initial description"}
    ).json()

    # Update both title and description
    response = client.patch(
        f"/tasks/{created['id']}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "done": True,
        },
    )

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
    created = client.post(
        "/tasks",
        json={"title": "Original title", "description": "Original description"},
    ).json()

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
    assert response.content == b""  # No content for 204 response

    # Verify the task is actually deleted
    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
