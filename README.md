# Task Board (CI/CD Demo)

A small full-stack Task Board app used as a hands-on CI/CD and DevOps learning project. See [CLAUDE.md](CLAUDE.md) for the full project spec and roadmap.

## Current status

FastAPI + PostgreSQL + Redis cache + basic Task CRUD, a React/TypeScript frontend, Dockerfiles for both, a Docker Compose stack, and a GitHub Actions CI pipeline (tests + build only — no AWS deployment yet).

## Backend setup (local, no Docker yet)

Requires Python 3.12+, a local PostgreSQL instance, and (optionally) a local Redis instance.

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp ../.env.example ../.env   # then edit DATABASE_URL / REDIS_URL if needed
```

`GET /api/tasks` caches results in Redis under the key `tasks:all` and invalidates
that key on any create/update/delete. If Redis isn't reachable, the API logs a
warning and falls back to querying PostgreSQL directly — Redis is optional
caching, not a hard dependency, so the app still works without it running.

Create the `tasks` database in PostgreSQL, then run the API:

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Running backend tests

Tests run against an in-memory SQLite database, so PostgreSQL is not required:

```bash
cd backend
pytest
```

## Running everything with Docker Compose

Requires Docker Desktop running.

```bash
docker compose up --build
```

This starts all four services (containers use service names to talk to each
other, e.g. `postgres`, `redis` — not `localhost`):

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Postgres data persists in the `postgres_data` named volume across restarts.
Stop everything with `docker compose down` (add `-v` to also drop the
Postgres volume).

## CI

`.github/workflows/ci-cd.yml` runs on every push/PR to `main`:

1. Backend tests (`pytest`)
2. Frontend type-check + build (`tsc -b && vite build`)
3. Docker image builds for `task-api` and `task-web`, tagged with the commit SHA, using Buildx with GitHub Actions layer caching (build only — not pushed anywhere yet). The `docker-build` job only runs if both test/build jobs above pass.
4. Each image is smoke-tested right after building: run the container, wait for it to respond (backend: `/health`, frontend: `/`), then tear it down. The backend smoke test points `DATABASE_URL` at a throwaway SQLite file so it doesn't need a real Postgres service in CI.

AWS ECR push and deployment are future milestones, not yet implemented.

## Local security scanning (Trivy)

[Trivy](https://trivy.dev) scans for known vulnerabilities in dependencies and
misconfigurations in the Dockerfiles. Install it (no admin rights required —
download the portable binary):

```bash
# Windows: download the zip from https://github.com/aquasecurity/trivy/releases
# and put trivy.exe somewhere on your PATH.
# macOS: brew install trivy
# Linux: see https://trivy.dev/latest/getting-started/installation/
```

Scan the repo (dependency vulnerabilities, Dockerfile misconfigurations, leaked secrets):

```bash
trivy fs --scanners vuln,secret,misconfig .
```

Scan a built image (after `docker compose build` or `docker build`):

```bash
docker compose build backend frontend
trivy image docker_container_project_2-backend
trivy image docker_container_project_2-frontend
```

Both Dockerfiles run as a non-root user and include a `HEALTHCHECK`, which
Trivy's misconfiguration checks verify.
