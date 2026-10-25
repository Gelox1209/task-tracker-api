# Task Tracker API

A REST API for managing tasks, built with **FastAPI**, **SQLAlchemy**, and **pytest**.

![Tests](https://github.com/gelox1209/task-tracker-api/actions/workflows/tests.yml/badge.svg)

## Features
- Create, list, and fetch tasks
- Input validation with clear error responses
- SQLite database (swappable for PostgreSQL)
- Automated tests with GitHub Actions CI
- User signup and JWT login

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") # App needs secret key to start
# Windows: $env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
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
| POST   | `/users`        | Create a user      | 201 / 409 |
| POST   | `/auth/token`   | Login/authenticate | 200 / 401 |
| GET    | `/tasks`        | List all tasks     | 200     |
| GET    | `/tasks/{id}`   | Get one task       | 200 / 404 |
| GET    | `/tasks?offset={≥0}&limit={1-100}&done={true/false}`| List tasks, paginated and filterable | 200 / 422 |
| PATCH  | `/tasks/{id}`   | Edit a task        | 200 / 422 / 404 |
| DELETE | `/tasks/{id}`   | Delete a task      | 204 / 404 |

## Project structure

```
app/
  main.py       # routes (the endpoints)
  models.py     # database tables (Task, User)
  schemas.py    # request/response validation
  security.py   # password hashing + JWT creation
  database.py   # DB connection + session
tests/
  conftest.py   # test setup (fresh DB per test, test SECRET_KEY)
  test_tasks.py # task endpoint tests
  test_users.py # signup tests
  test_auth.py  # login + token tests
.github/workflows/tests.yml  # CI: tests, lint, and format check on every push and PR
requirements.txt             # Python dependencies
```

## Tech stack

| Area | Tools |
|------|-------|
| Language | Python 3.12 |
| Web framework | FastAPI, served by Uvicorn |
| Database | SQLite via SQLAlchemy 2.0 (ORM) |
| Validation | Pydantic v2 |
| Auth | PyJWT (HS256 tokens), pwdlib with Argon2 (password hashing), python-multipart (login form) |
| Testing | pytest, pytest-cov, FastAPI TestClient (httpx) |
| Code quality | Ruff (linting + formatting) |
| CI | GitHub Actions |

## Roadmap
- [x] `PATCH /tasks/{id}` and `DELETE /tasks/{id}`
- [x] Filtering (`?done=true`) and pagination
- [ ] User accounts with JWT auth
- [ ] PostgreSQL + Docker
- [ ] Deploy to Render or Railway
