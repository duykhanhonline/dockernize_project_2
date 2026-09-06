# CLAUDE.md

## Project Overview

This project is a small full-stack Task Board / Todo application designed primarily as a hands-on CI/CD and DevOps learning project.

The application itself should remain intentionally simple.

Main goals:
- Python backend development with FastAPI
- React + TypeScript frontend development
- PostgreSQL
- Redis caching
- Docker and Docker Compose
- Automated testing
- GitHub Actions CI/CD
- Docker image versioning
- AWS ECR
- Later deployment to AWS ECS/Fargate

Do not introduce unnecessary application complexity unless explicitly requested.

## Technology Stack

### Backend
- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- PostgreSQL
- Redis
- pytest

### Frontend
- React
- TypeScript
- Vite
- Fetch API or Axios
- Basic CSS

Avoid introducing large UI frameworks unless explicitly requested.

### Infrastructure
- Docker
- Docker Compose
- GitHub Actions
- AWS ECR

Future deployment may use AWS ECS, AWS Fargate, and an Application Load Balancer.
Do not implement AWS deployment infrastructure unless requested.

## Project Structure

Preferred structure:

```text
cicd-demo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── redis_client.py
│   │   └── config.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskList.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

Keep the structure simple. Do not introduce microservices.

## Application Requirements

The application is a simple Task Board.

A task contains:

```json
{
  "id": 1,
  "title": "Deploy application",
  "completed": false,
  "created_at": "2026-09-05T19:00:00"
}
```

Required functionality:
1. Create a task
2. List tasks
3. Update a task
4. Mark a task as completed/uncompleted
5. Delete a task

No authentication is required.

Do not add user accounts, OAuth, JWT, roles, permissions, WebSockets, messaging queues, or microservices unless explicitly requested.

## Backend API

Base API path: `/api`

Required endpoints:

```text
GET    /api/tasks
GET    /api/tasks/{id}
POST   /api/tasks
PUT    /api/tasks/{id}
DELETE /api/tasks/{id}
GET    /health
```

The health endpoint should be simple and useful for Docker/AWS health checks.

Example:

```json
{"status": "healthy"}
```

## PostgreSQL

PostgreSQL is the persistent data store.

Conceptual tasks table:

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Prefer SQLAlchemy models instead of manually writing SQL throughout the application.

Database configuration must come from environment variables.

Example:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tasks
```

Never hard-code production database credentials.

## Redis

Redis is used only as a simple caching layer. Do not use Redis as the primary database.

For `GET /api/tasks`:
1. Check Redis.
2. If cache exists, return cached tasks.
3. Otherwise query PostgreSQL.
4. Store result in Redis.
5. Return tasks.

Use a simple cache key such as `tasks:all`.

When a task is created, updated, or deleted, update PostgreSQL and delete the `tasks:all` cache key.

Keep caching simple and easy to understand.

## Frontend

The frontend should remain minimal.

Required functionality:
- Display tasks
- Add task
- Toggle completed status
- Delete task
- Show basic loading state
- Show basic API error message

Avoid complicated state management. Prefer React hooks such as `useState` and `useEffect`.
Do not introduce Redux unless explicitly requested.

## Local Development Strategy

Recommended implementation order:

```text
1. FastAPI
2. PostgreSQL
3. Backend CRUD
4. Backend tests
5. React + TypeScript
6. Connect frontend to API
7. Redis
8. Dockerize backend
9. Dockerize frontend
10. Docker Compose
11. GitHub Actions CI
12. AWS ECR
13. AWS deployment
```

Do not skip ahead unless explicitly requested.

## Local URLs

During non-Docker local development:

```text
Frontend:        http://localhost:5173
Backend:         http://localhost:8000
FastAPI Swagger: http://localhost:8000/docs
PostgreSQL:      localhost:5432
Redis:           localhost:6379
```

## Environment Variables

Example `.env.example`:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tasks
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:5173
```

Never commit `.env` files containing secrets. Commit only `.env.example`.

## Docker

The final local development environment should support:

```bash
docker compose up --build
```

Services:
- frontend
- backend
- postgres
- redis

Within Docker Compose, containers must communicate using service names.

Use:
```text
postgresql://postgres:postgres@postgres:5432/tasks
redis://redis:6379
```

Do not use localhost for communication between containers.

## Testing

Backend tests should use pytest.

At minimum test:
- GET /health
- POST /api/tasks
- GET /api/tasks
- PUT /api/tasks/{id}
- DELETE /api/tasks/{id}

CI should fail when tests fail.

Frontend testing should remain lightweight because the primary goal is CI/CD practice.

## CI/CD Goals

Expected pipeline:

```text
git push
    ↓
GitHub Actions
    ↓
Backend tests
    ↓
Frontend build/type check
    ↓
Docker build
    ↓
Authenticate with AWS
    ↓
Login to ECR
    ↓
Push Docker images
    ↓
AWS ECR
```

Do not push images to ECR when required tests fail.

## Docker Image Strategy

There should eventually be two application images:
- task-api
- task-web

Images should be tagged with the Git commit SHA, for example:

```text
task-api:8f42cd1
task-web:8f42cd1
```

Optionally also maintain `latest` tags.

Git SHA tags should be preferred for identifying exact deployments.

## AWS Authentication

For GitHub Actions, prefer GitHub Actions OIDC with an AWS IAM role when implementing the AWS stage.

Avoid long-lived AWS access keys where practical.

Never:
- Commit AWS credentials
- Put credentials in Dockerfiles
- Put credentials in source code
- Print secrets in CI logs

## AWS ECR

The first AWS milestone is only:

```text
GitHub Actions
      ↓
Docker Build
      ↓
AWS ECR
```

Do not automatically introduce ECS, EKS, Terraform, Kubernetes, or other infrastructure during this milestone.

## Future Deployment

After ECR is working successfully, the preferred next deployment target is ECS Fargate.

PostgreSQL may later move to RDS and Redis may later move to ElastiCache.

These are future enhancements and should not be introduced during initial local development.

## Coding Guidelines

### Python
Prefer:
- Type hints
- Small functions
- Pydantic schemas
- FastAPI dependency injection
- Clear variable names

Avoid unnecessary abstractions and enterprise-style architecture.

### TypeScript
Avoid `any` where reasonable.

Example:

```typescript
export interface Task {
  id: number;
  title: string;
  completed: boolean;
  created_at: string;
}
```

Keep components small.

## Error Handling

Use appropriate HTTP status codes such as:
- 200 OK
- 201 Created
- 400 Bad Request
- 404 Not Found
- 422 Validation Error
- 500 Internal Server Error

Do not expose database credentials, stack traces, AWS credentials, or internal secrets to clients.

## Logging

Use normal application logging instead of excessive `print()` statements.

Logs should help diagnose application startup, database connectivity, Redis connectivity, and API errors.

Never log passwords or secrets.

## Health Check

Implement `GET /health`.

This endpoint may later be used by Docker, CI/CD verification, AWS ECS, and the Application Load Balancer.

Keep it fast.

## Git Workflow

Use small, understandable commits, for example:

```text
feat: initialize FastAPI backend
feat: add PostgreSQL task model
feat: implement task CRUD endpoints
test: add task API tests
feat: create React task interface
feat: add Redis task cache
build: add backend Dockerfile
build: add frontend Dockerfile
build: add Docker Compose
ci: add backend tests
ci: build Docker images
ci: push images to AWS ECR
```

## Important Instructions for Claude Code

When working on this repository:

1. Read this CLAUDE.md before making architectural decisions.
2. Keep the project intentionally simple.
3. Do not introduce new frameworks, services, or architectural patterns unless necessary.
4. Before adding a dependency, explain why it is necessary.
5. Prefer modifying existing files over creating unnecessary abstractions.
6. Do not implement authentication unless explicitly requested.
7. Do not introduce microservices.
8. Do not introduce Kubernetes at this stage.
9. Do not introduce Terraform at this stage.
10. Do not create AWS resources unless explicitly requested.
11. Never hard-code credentials or secrets.
12. Maintain compatibility with local development.
13. Maintain compatibility with Docker Compose.
14. When changing API behavior, consider whether tests need updating.
15. When changing database models, explain whether a migration is required.
16. When modifying Docker or CI/CD configuration, explain what the change does.
17. Prefer commands that work on Windows/WSL/Linux where practical.
18. Do not refactor unrelated code while implementing a requested feature.
19. Keep README instructions synchronized with major setup changes.
20. If a requirement is ambiguous, prefer the simplest implementation.

## Learning Objective

This repository is intended to demonstrate:

```text
Code
 ↓
Test
 ↓
Build
 ↓
Containerize
 ↓
CI
 ↓
Container Registry
 ↓
Deploy
 ↓
Monitor
```

The most important learning areas are Git workflow, automated tests, Docker, Docker Compose, GitHub Actions, AWS authentication, AWS ECR, image tagging, deployment automation, and rollback concepts.

Application complexity should remain secondary.

## Current Development Phase

Current phase:

```text
LOCAL DEVELOPMENT
```

Priority:

```text
FastAPI
   ↓
PostgreSQL
   ↓
Basic Task CRUD
```

Do not implement Redis, Docker, GitHub Actions, or AWS ECR until the basic backend CRUD functionality is working locally, unless explicitly requested.
