"""API entry point. Run with:  uvicorn app.main:app --reload"""
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

# Creates tables on startup. Fine for learning; real projects use migrations (Alembic).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Tracker API", version="0.1.0")


@app.get("/health")
def health():
    """Simple check that the server is running (hosting platforms ping this)."""
    return {"status": "ok"}


@app.post("/tasks", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_in: schemas.TaskCreate, db: Annotated[Session, Depends(get_db)]):
    task = models.Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)  # reload so id and created_at are filled in
    return task


@app.get("/tasks", response_model=list[schemas.TaskRead])
def list_tasks(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(models.Task).order_by(models.Task.id)).all()


@app.get("/tasks/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, task_in: schemas.TaskUpdate, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()