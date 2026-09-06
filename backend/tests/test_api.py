import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task():
    response = client.post("/api/tasks", json={"title": "Deploy application"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Deploy application"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks():
    client.post("/api/tasks", json={"title": "Task A"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_task_not_found():
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_update_task():
    create_resp = client.post("/api/tasks", json={"title": "Task to update"})
    task_id = create_resp.json()["id"]

    response = client.put(f"/api/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task():
    create_resp = client.post("/api/tasks", json={"title": "Task to delete"})
    task_id = create_resp.json()["id"]

    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404
