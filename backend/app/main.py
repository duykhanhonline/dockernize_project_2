import json
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis import RedisError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.database import Base, engine, get_db
from app.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TASKS_CACHE_KEY = "tasks:all"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured")
    except Exception:
        logger.exception("Failed to connect to the database on startup")
        raise
    yield


app = FastAPI(title="Task Board API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def invalidate_tasks_cache() -> None:
    try:
        redis_client.delete(TASKS_CACHE_KEY)
    except RedisError:
        logger.warning("Could not invalidate tasks cache in Redis", exc_info=True)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/tasks", response_model=list[schemas.TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    try:
        cached = redis_client.get(TASKS_CACHE_KEY)
    except RedisError:
        logger.warning("Could not read tasks cache from Redis", exc_info=True)
        cached = None

    if cached is not None:
        return json.loads(cached)

    tasks = crud.get_tasks(db)
    serialized = [
        schemas.TaskOut.model_validate(task).model_dump(mode="json") for task in tasks
    ]

    try:
        redis_client.set(TASKS_CACHE_KEY, json.dumps(serialized))
    except RedisError:
        logger.warning("Could not write tasks cache to Redis", exc_info=True)

    return serialized


@app.get("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud.create_task(db, task)
    invalidate_tasks_cache()
    return db_task


@app.put("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    task = crud.update_task(db, task_id, task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    invalidate_tasks_cache()
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    invalidate_tasks_cache()
