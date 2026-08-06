# colore-os

AI Administrator for Beauty Salons

## Deployment Source of Truth

| | |
|---|---|
| **Working repository** | `/root/colore-os` |
| **Working compose** | `/opt/colore-os/docker/docker-compose.yml` |
| **Build context** | `/root/colore-os/backend` |
| **Container env file** | `/opt/colore-os/docker/.env` |

`/opt/colore-os/app` is an **archived** second clone of this repository, pinned to a July commit. It must never be used as a build context — doing so ships an application that predates the current one.

## Rebuild and restart the backend

```bash
cd /opt/colore-os/docker
GIT_COMMIT=$(git -C /root/colore-os rev-parse --short HEAD) docker compose build backend
docker compose up -d backend
```

`GIT_COMMIT` is optional; without it the container reports `unknown`.

## Verify

```bash
scripts/doctor.sh
```

Checks build context, image and commit, configuration, `/docs`, `/ui/`, PostgreSQL, the conversation endpoint and pytest database isolation. Prints `✅ SYSTEM HEALTHY` (exit 0) or a numbered list of problems (exit 1). It only reads — it never fixes, rebuilds, restarts or creates data. Run it before a demo.

```bash
docker logs colore-backend 2>&1 | head -20
```

On start the backend logs its version, git commit, build context, and whether `OPENAI_API_KEY` is set (`YES`/`NO` — the key itself is never logged). If `/ui` is missing or `app/static/` did not reach the image, an `ERROR` line explains why. Missing required configuration (`OPENAI_API_KEY`, `POSTGRES_HOST`, `POSTGRES_DB`, `ALTEGIO_BASE_URL`) stops startup with a readable message.

## Run tests

```bash
cd /root/colore-os/backend && source .venv/bin/activate && python -m pytest app/tests/ -q
```

Tests never touch the working database. They use `TEST_DATABASE_URL`, or a temporary SQLite file when it is not set.
