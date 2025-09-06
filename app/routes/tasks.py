from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, database
from app.routes.auth import get_current_user

router = APIRouter()


# -------------------------
# DB session dependency
# -------------------------
def get_db():
    db = database.get_db()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Create a new task
# -------------------------
@router.post("/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    tags_str = ",".join(task.tags) if getattr(task, "tags", None) else None
    new_task = models.Task(
        **task.dict(exclude={"tags"}), 
        tags=tags_str,
        owner_username=username
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# -------------------------
# Update a task
# -------------------------
@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_username == username
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority
    db_task.tags = ",".join(task.tags) if getattr(task, "tags", None) else None

    db.commit()
    db.refresh(db_task)
    return db_task


# -------------------------
# List tasks for current user with pagination
# -------------------------
@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    tasks = (
        db.query(models.Task)
        .filter(models.Task.owner_username == username)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tasks


# -------------------------
# Delete a task
# -------------------------
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_username == username
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}
