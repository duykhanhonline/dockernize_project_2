from sqlalchemy.orm import Session

from app import models, schemas


def get_tasks(db: Session) -> list[models.Task]:
    return db.query(models.Task).order_by(models.Task.id).all()


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session, task_id: int, task_update: schemas.TaskUpdate
) -> models.Task | None:
    db_task = get_task(db, task_id)
    if db_task is None:
        return None

    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.completed is not None:
        db_task.completed = task_update.completed

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if db_task is None:
        return False

    db.delete(db_task)
    db.commit()
    return True
