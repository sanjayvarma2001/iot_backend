# Backend (FastAPI) — Workflow

## Overview

This backend is a FastAPI application that provides the REST API for the MQTT Device Full Stack project. It connects to a MySQL database and publishes/subscribes to the MQTT broker configured in the Docker Compose stack.

## Key files

- `main.py` — FastAPI app entrypoint.
- `model.py` / `db.py` — database models and helper functions.
- `requirements.txt` — Python dependencies used by the Docker image.
- `Dockerfile` — builds the backend image used by `docker-compose.yml`.

## Local development (without Docker)

1. Create a virtual environment and activate it.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set environment variables (example):

```powershell
$env:DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/iot_db"
$env:MQTT_BROKER_HOST = "localhost"
```

4. Run the app with uvicorn:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

## Docker / Compose (recommended for full stack)

- Build the backend image and start services with:

```powershell
docker-compose build backend
docker-compose up -d backend
```

- Or start the whole stack (db, mqtt, backend, frontend):

```powershell
docker-compose up --build
```

The `docker-compose.yml` sets the `DATABASE_URL` and `MQTT_BROKER_HOST` for the `backend` service so it can connect to the `db` and `mqtt_broker` services defined in the same compose file.

## Environment variables used

- `DATABASE_URL` — SQLAlchemy connection string (example: `mysql+pymysql://user:password@db:3306/iot_db`).
- `MQTT_BROKER_HOST` — hostname for the MQTT broker service (compose sets this to `mqtt_broker`).

## Troubleshooting

- If the backend cannot connect to the database, ensure the `db` service is up and the MySQL data folder (`mysql_data/`) has correct permissions.
- For dependency or import errors, recreate the environment and reinstall `requirements.txt`.

## Notes

- Unit tests are not included by default; consider adding tests for critical API endpoints.
- If you change models or DB schema, add migration steps (e.g., Alembic) to manage schema changes.
