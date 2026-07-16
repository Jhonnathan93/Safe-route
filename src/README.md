# Safe Route

A web application for finding pedestrian routes in Medellín with lower exposure to harassment risk. It turns the console deliveries into a modern REST API and map interface.

## Architecture

- `backend/`: Django + Django REST Framework. It loads the CSV once, creates a **bidirectional** pedestrian graph, and runs Dijkstra's algorithm.
- `frontend/`: React + TypeScript + Leaflet. It searches places, displays the route, and lets users balance safety and distance.
- `backend/data/`: backend-owned street dataset bundled with the Django service.
- `docker-compose.yml`: runs both services.

## Run with Docker

Copy `.env.example` to `.env` and replace its values. Then, from this directory:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The API is available at `http://localhost:8000/api/`.

The dataset is part of the backend at `backend/data/calles_de_medellin_con_acoso.csv`. The backend image includes it, so Docker Compose and serverless deployments use the same default path. Set `DATASET_PATH` only when you intentionally provide the CSV from another location.

## Local development

Backend (Python 3.12 recommended):

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
set DATASET_PATH=data/calles_de_medellin_con_acoso.csv
set DJANGO_SECRET_KEY=a-long-random-secret
set GEOCODER_USER_AGENT=safe-route-contact@example.com
.venv/Scripts/python manage.py runserver
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

## Risk model and corrections

Every segment has a normalized 0–100 risk score. Route exposure is the length-weighted average: `sum(risk * length) / sum(length)`. The optimizer uses `meters * (1 + riskWeight * normalizedRisk)`; the 0–10 factor is controlled in the interface. At 0 it favors distance; at 10 it favors safety.

The graph adds both directions for every row regardless of `oneway`: pedestrians can walk a street in either direction. It also preserves parallel edges and uses a priority queue, unlike the earlier implementations.

Search uses Nominatim (OpenStreetMap), limited to Medellín. When no geocoded result exists, the interface asks the user to select an approximate point on the map; the route service then snaps that point to the nearest graph node.

## Backend decisions

- Views are in `routing/views/` and only validate, coordinate, and respond with the shared envelope.
- Stateless utilities are in `routing/utils/`, use PascalCase modules, and expose static methods.
- `PedestrianRoutingService` owns the graph cache; its initialization is centralized in `routing/services/ServiceContainer.py`.
- `DatasetValidator` requires the `origin`, `destination`, `length`, and `harassmentRisk` columns before building the graph.

## Endpoints

- `GET /api/routing/geocode/?q=Parque+Lleras`: geocoded result and nearest graph node.
- `POST /api/routing/routes/`:

```json
{
  "origin": { "lat": 6.208, "lng": -75.571 },
  "destination": { "lat": 6.217, "lng": -75.568 },
  "risk_weight": 5
}
```

All responses use the `{ "success", "message", "data" }` envelope. Validation errors use the same shape and provide per-field details inside `data`.

Current endpoints are public because they do not modify data. This policy is declared explicitly in DRF configuration; any future upload or modification endpoint must require specific authentication and permissions.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATASET_PATH` | `data/calles_de_medellin_con_acoso.csv` | Street-network CSV |
| `DJANGO_SECRET_KEY` | — | Required Django secret |
| `DJANGO_ALLOWED_HOSTS` | — | Comma-separated allowed hosts |
| `DJANGO_SECURE_SSL_REDIRECT` | `true` in production | Forces HTTPS in the production profile |
| `GEOCODER_USER_AGENT` | — | Required Nominatim identifier |
| `VITE_API_URL` | `http://localhost:8000/api` | Frontend API URL |

## Tests

The backend uses `pytest` and covers the bidirectional graph, risk metric, and API envelope. Run:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
ruff check .
```
