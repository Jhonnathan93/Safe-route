# Safe Route

Safe Route is a web application that helps people explore pedestrian routes in Medellín while balancing walking distance and an estimated street-harassment risk. It evolves an academic graph-algorithm project into a containerized React and Django REST application with an interactive map.

> **Important:** risk scores are data-driven estimates, not a guarantee of personal safety. Always use local knowledge and make decisions appropriate to current conditions.

## Purpose

Street harassment and perceived insecurity can affect how people move through a city. This project models Medellín streets as a pedestrian graph and finds routes with a tunable trade-off between distance and estimated risk exposure.

The original project evaluated three Dijkstra variants:

- shortest distance;
- lowest harassment risk;
- a weighted combination of distance and risk.

The current application keeps the same problem focus while providing a maintainable API, a browser interface, geocoding, and a clear route-risk metric.

## Current application

The actively maintained application lives in [`src/`](src/).

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Frontend | React, TypeScript, React Query, Leaflet | Location search, map interaction, route visualization, and local UI state |
| Backend | Django, Django REST Framework | Input validation, geocoding coordination, route API, and response contract |
| Routing domain | Python | CSV validation, graph construction, Dijkstra calculation, and risk aggregation |
| Deployment | Docker Compose, Gunicorn, Nginx | Portable local deployment |

### Main capabilities

- Search origin and destination with Nominatim/OpenStreetMap geocoding.
- Select a point directly on the map when a geocoding query has no reliable result.
- Snap requested locations to the nearest node in the pedestrian graph.
- Calculate a route using a safety-priority slider from 0 (shortest) to 10 (safest).
- Display route distance, weighted average risk, and the route geometry on a Leaflet map.
- Return all API responses with a consistent `success`, `message`, and `data` envelope.

## How routing works

### Pedestrian graph

The street network is loaded from [`src/backend/data/calles_de_medellin_con_acoso.csv`](src/backend/data/calles_de_medellin_con_acoso.csv). Every row becomes two edges:

```text
origin <--> destination
```

This is intentional. The application is designed for walking, so a street is traversable in both directions even if the original road metadata marks it as one-way for vehicles.

The graph is represented as an adjacency list, built when Django starts, and retained as a read-only in-memory structure by the backend service. It preserves parallel segments, validates required CSV columns, and uses Dijkstra's algorithm with a priority queue. Gunicorn preloads the graph before creating workers so they inherit the initialized representation without re-reading the CSV per request.

### Risk and route cost

The source `harassmentRisk` values are normalized to a 0–100 scale. Missing values use the dataset average. Route exposure is reported as a length-weighted average:

```text
route risk = sum(segment risk × segment length) / sum(segment length)
```

For route selection, each segment uses this cost:

```text
segment cost = length in meters × (1 + safety weight × normalized risk / 100)
```

At weight `0`, the route favors distance. Higher weights increasingly avoid higher-risk segments.

## Dataset and research background

The historical reports describe a Medellín network obtained from OpenStreetMap/OSMnx. Each street segment includes its length, direction metadata, and geometry. The original risk estimate was derived from Medellín's 2017 Quality of Life Survey using indicators related to perceived insecurity and households below one minimum wage, followed by normalization.

The historical deliverables and their visualizations remain available for reference:

- [`Presentaciones/`](Presentaciones/)
- [`Reportes tecnicos/`](Reportes%20tecnicos/)
- [`code/SegundaEntrega/`](code/SegundaEntrega/)
- [`code/TerceraEntrega/`](code/TerceraEntrega/)

They document the academic evolution of the algorithm. The new implementation in `src/` is the recommended version to run.

## Quick start with Docker

### 1. Create the environment file

From `src/`, copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

For local development, use the following values:

```env
DJANGO_SECRET_KEY=dev-only-safe-route-secret-2026-change-in-production
GEOCODER_USER_AGENT=safe-route-local-development/1.0
```

### 2. Start the application

```powershell
cd src
docker compose up --build
```

Open:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000/api/>

## Deploy on Vercel

[`src/vercel.json`](src/vercel.json) deploys the React frontend and Django backend together as Vercel Services: `/api/*` is routed to Django and all other requests go to the frontend. Import the repository as one Vercel project and set its Root Directory to `src`.

Set these Production environment variables before deploying:

```env
DJANGO_SECRET_KEY=<a-long-random-private-value>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<your-project>.vercel.app
GEOCODER_USER_AGENT=safe-route/1.0 (your-email@example.com)
GEOCODER_TIMEOUT_SECONDS=8
EAGER_GRAPH_WARM_UP=false
VITE_API_URL=/api
```

Do not configure `CORS_ALLOWED_ORIGINS`: both services use the same public origin. For Preview deployments, set `DJANGO_ALLOWED_HOSTS=.vercel.app`.

To stop the application:

```powershell
docker compose down
```

## Using the application

1. Enter an origin and select **Search**.
2. Enter a destination and select **Search**.
3. If a place is not found, select **Select point on map**, then click its approximate location on the map.
4. Set the safety priority.
5. Select **Calculate safe route**.

The selected points are snapped to the graph before routing, so the displayed route starts and ends on available pedestrian segments.

## API

Base path: `/api/routing/`

### Geocode a place

```http
GET /api/routing/geocode/?q=Parque%20Lleras
```

### Calculate a route

```http
POST /api/routing/routes/
Content-Type: application/json

{
  "origin": { "lat": 6.208, "lng": -75.571 },
  "destination": { "lat": 6.217, "lng": -75.568 },
  "risk_weight": 6
}
```

Successful responses follow this shape:

```json
{
  "success": true,
  "message": "Route calculated successfully.",
  "data": {}
}
```

## Local development

### Backend

```powershell
cd src/backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt
$env:DJANGO_SECRET_KEY="dev-only-safe-route-secret-2026-change-in-production"
$env:GEOCODER_USER_AGENT="safe-route-local-development/1.0"
pytest
ruff check .
.venv/Scripts/python manage.py runserver
```

### Frontend

```powershell
cd src/frontend
npm install
npm run dev
npm run lint
npm run format:check
```

The frontend uses a single API client, Zod response validation, React Query for server state, localized component state, error boundaries, absolute imports, ESLint, and Prettier. The Leaflet map is lazy-loaded to reduce the initial JavaScript payload.

## Project layout

```text
Safe-route/
├── src/                         # Current web application
│   ├── backend/                  # Django REST backend
│   ├── data/                     # Street network CSV
│   ├── frontend/                 # React application
│   └── docker-compose.yml
├── code/                         # Historical algorithm deliveries
├── Presentaciones/               # Original project presentations
└── Reportes tecnicos/            # Original technical reports
```

## Limitations and next steps

- The source risk data is historical and should be refreshed before operational or city-wide use.
- A missing geocoding result requires a map click because arbitrary text alone does not provide a trustworthy geographic coordinate.
- Future work described in the original deliverables includes richer safety variables, accessibility, traffic and time-of-day information, additional cities, mobile interfaces, and continuously updated models.

## Author

Jhonnathan Ocampo
