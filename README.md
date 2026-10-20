# ALP Attendance Service — CI/CD demo

A small service from the AMWA Adult Literacy/ESL Program (ALP) management platform
(CSE 485 capstone). It records class sessions and student check-ins and flags any
student whose attendance falls below 75% so the program manager can follow up.

Built for the CSE 485 "Growing a Competency" assignment: **CI/CD pipeline with
GitHub Actions & Docker**.

## Pipeline (`.github/workflows/ci-cd.yml`)
1. **lint** — ruff lint + format check
2. **test** — pytest (unit + integration) on Python 3.11 and 3.12, fails under 90% coverage
3. **build-and-smoke-test** — builds the multi-stage Docker image, runs it, checks `/health`
4. **deliver** — on `main` only, pushes the image to GitHub Container Registry

## Run locally
```bash
pip install -r requirements-dev.txt && pytest -v
docker compose up --build      # http://localhost:8000/health
```

## API
| Method | Path | Purpose |
|---|---|---|
| GET | /health | liveness check |
| POST | /students | `{name, level}` |
| POST | /sessions | `{level, date}` |
| POST | /sessions/{id}/checkins | `{student_id}` |
| GET | /reports/attendance | rates, lowest first, with follow-up flags |
