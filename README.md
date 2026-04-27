# Suanchao

[English](./README.md) | [中文](./README_CN.md)

Suanchao is an online programming practice platform for Chinese users, featuring online judging, AI problem generation, AI tutoring, a problem sharing square, wrong-answer review, and bilingual UI (Chinese/English).

## Features

- Online Judge: support both submission judging and custom input run.
- AI Problem Generation: estimate difficulty from your progress or generate by custom level.
- Private AI Problem Set: AI-generated problems are private per user and separated from the official bank.
- Problem Square: share solved problems, import others' problems, and sort by stars.
- Discussion System: topic discussion, comments, and owner-side comment deletion.
- Wrong-Answer Book: review by tags and due schedule with second-round reminders.
- Bilingual UI: switch between Chinese and English.

## Tech Stack

- Frontend: Vue 3 + Vite + Pinia + Vue Router + Monaco Editor
- Backend: FastAPI + SQLAlchemy (async) + Alembic
- Database: PostgreSQL
- Queue/Cache: Redis

## Project Structure

```text
.
├── app/                 # FastAPI backend
├── frontend/            # Vue frontend
├── alembic/             # Database migrations
├── scripts/             # Ops / migration scripts
├── deploy/              # Docker/Podman build files and Nginx config
├── docker-compose.yml   # Container orchestration
└── DEPLOY_DOCKER.md     # Cloud deployment guide
```

## Local Development

### 1) Backend

```bash
cd /path/to/suanchao
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` as needed (database, AI, SMTP, etc.).

### 2) Prepare DB and Run Migrations

```bash
python scripts/migrate.py upgrade head
```

### 3) Start Backend

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 30881
```

### 4) Start Frontend

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 30880
```

Access:

- Frontend: `http://127.0.0.1:30880`
- Backend health: `http://127.0.0.1:30881/health`

## Container Deployment (Recommended for Cloud)

Docker / Podman Compose is included:

```bash
cp .env.cloud.example .env
podman compose up -d --build
```

Or:

```bash
docker compose up -d --build
```

See [DEPLOY_DOCKER.md](./DEPLOY_DOCKER.md) for full deployment details.

## Database Migration

Common commands:

```bash
python scripts/migrate.py upgrade head
python scripts/migrate.py current
python scripts/migrate.py history
python scripts/migrate.py downgrade -1
```

Detailed migration notes: [MIGRATIONS.md](./MIGRATIONS.md)

## Security Notes

- Do not commit `.env`, database backups, or log files.
- Rotate all secrets before production (`SECRET_KEY`, `OPENAI_API_KEY`, `SMTP_PASSWORD`, etc.).
