# Task Tracker API

A REST API for managing tasks, built with **FastAPI**, **SQLAlchemy**, and **pytest**.

![Tests](https://github.com/gelox1209/task-tracker-api/actions/workflows/tests.yml/badge.svg)

## Features
- Create, list, and fetch tasks
- Input validation with clear error responses
- SQLite database (swappable for PostgreSQL)
- Automated tests with GitHub Actions CI

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs where you can try every endpoint.

## Run tests

```bash
pytest                                  # run all tests
pytest --cov=app --cov-report=term-missing   # see which lines aren't tested
```

## Endpoints

| Method | Path            | Description        | Success |
|--------|-----------------|--------------------|---------|
| GET    | `/health`       | Health check       | 200     |
| POST   | `/tasks`        | Create a task      | 201     |
| GET    | `/tasks`        | List all tasks     | 200     |
| GET    | `/tasks/{id}`   | Get one task       | 200 / 404 |
| GET    | `/tasks?offset=`| Get tasks with offset, 0 or more  | 200 / 422 |
| GET    | `/tasks?offset={>0}&limit={1-100}&done={True/False}`| List tasks, paginated and filterable | 200 / 422 |
| GET    | `/tasks?done=`  | Get tasks that is done or not done  | 200 / 422 |
| PATCH  | `/tasks/{id}`   | Edit a task        | 200 / 422 / 404 |
| DELETE | `/tasks/{id}`   | Delete a task      | 204 / 404 |

## Project structure

```
app/
  main.py       # routes (the endpoints)
  models.py     # database tables
  schemas.py    # request/response validation
  database.py   # DB connection + session
tests/
  conftest.py   # test setup (fresh DB per test)
  test_tasks.py # endpoint tests
.github/workflows/tests.yml  # CI: runs tests on every push
```

## Roadmap
- [x] `PATCH /tasks/{id}` and `DELETE /tasks/{id}`
- [x] Filtering (`?done=true`) and pagination
- [ ] User accounts with JWT auth
- [ ] PostgreSQL + Docker
- [ ] Deploy to Render or Railway
