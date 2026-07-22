# HomeScape

A microservices real-estate marketplace, built as a system-design portfolio
project: buyers search and inquire about homes, sellers and agents list and
manage properties, and every service owns exactly one business domain and
talks to the others over an event bus or a small internal API - never
by sharing a database.

Backend: **Django REST Framework, PostgreSQL, Redis, Elasticsearch.**
Frontend: **React + Vite.**

## Architecture

```mermaid
flowchart TB
    Client["Browser<br/>React + Vite frontend"]

    Client --> Gateway["Nginx Gateway<br/><sub>routing · rate limiting · CORS</sub>"]

    subgraph Services["Microservices"]
        direction LR
        Auth["Auth Service<br/><sub>:4001</sub>"]
        Property["Property Service<br/><sub>:4002</sub>"]
        Search["Search Service<br/><sub>:4003</sub>"]
        Inquiry["Inquiry Service<br/><sub>:4004</sub>"]
        Media["Media Service<br/><sub>:4005</sub>"]
    end

    Gateway -->|/api/auth| Auth
    Gateway -->|/api/properties| Property
    Gateway -->|/api/search| Search
    Gateway -->|/api/inquiries| Inquiry
    Gateway -->|/api/media| Media

    Inquiry -.->|"resolves seller_id"| Property

    Notify["Notification Service<br/><sub>:4006 · no gateway route, event-driven only</sub>"]

    Auth --> AuthDB[("Postgres · auth_db")]
    Property --> PropertyDB[("Postgres · property_db")]
    Inquiry --> InquiryDB[("Postgres · inquiry_db")]
    Search --> ES[("Elasticsearch")]
    Media --> Store[("local disk / S3")]
    Notify --> Mail[["SMTP or console"]]

    classDef svc fill:#14213D,stroke:#0A1526,color:#fff
    classDef store fill:#F5F3EE,stroke:#B08946,color:#14213D
    class Auth,Property,Search,Inquiry,Media,Notify svc
    class AuthDB,PropertyDB,InquiryDB,ES,Store,Mail store
```

The dotted arrow is the one direct service-to-service HTTP call in the
system - Inquiry Service asking Property Service for a listing's
`seller_id` before saving a message. Everything else that looks like it
should be a direct call instead goes through the event bus, so Property
Service never needs to know Search Service or Notification Service exist:

```mermaid
sequenceDiagram
    participant P as Property Service
    participant R as Redis Pub/Sub
    participant S as Search Service
    participant N as Notification Service

    P->>R: publish PropertyCreated
    par fan-out, each subscriber independent
        R-->>S: PropertyCreated
        R-->>N: PropertyCreated
    end
    S->>S: index the listing in Elasticsearch
    N->>N: email the seller "your listing is live" (or log to console)
```

Full event catalog: `UserRegistered` · `PropertyCreated` ·
`PropertyUpdated` · `PropertyDeleted` · `PropertyViewed` ·
`InquiryCreated` · `InquiryResponded`.

## Services

| Service | Owns | Port |
|---|---|---|
| `auth-service` | users, roles, sessions/refresh tokens, audit log | 4001 |
| `property-service` | properties, images metadata, amenities, favorites | 4002 |
| `search-service` | Elasticsearch index, full-text/geo/filtered search, autocomplete | 4003 |
| `inquiry-service` | messages, viewing requests, offers | 4004 |
| `media-service` | image uploads (local disk by default, S3 when configured) | 4005 |
| `notification-service` | reacts to events, sends email (or logs if SMTP isn't set) | 4006 |
| `gateway` (Nginx) | single entrypoint, routes `/api/*` to the service above | 8080 |
| `frontend` | React app (buyer search/detail flow + seller dashboard) | 3000 |

Each service owns its own Postgres database (or Elasticsearch index) - no
shared schema, no cross-service joins. This is the same event-driven,
service-boundary approach described in the original design doc.

### Stateless JWT auth

Only Auth Service has a real `User` table. Every other service verifies
the same HS256-signed token locally via a small `jwt_auth.py` (copied into
each service, like the Redis event-bus helper) - no per-request call back
to Auth Service.

Property listing detail is a public `GET` but an owner-only
`PATCH`/`DELETE` on the same URL. DRF's default behavior on a
failed/absent authentication is to set `request.user` to Django's
`AnonymousUser` - which is truthy and has no `.role` attribute, so `if not
request.user` would silently do the wrong thing and `request.user.role`
would throw. Setting `UNAUTHENTICATED_USER = None` in settings (see every
service's `config/settings.py`) makes `request.user` reliably `None`
instead, so the ownership checks behave correctly for both anonymous and
authenticated requests on the same endpoint.

### Gateway routing

A handful of endpoints are called at the bare resource path with nothing
after it - `GET /api/properties` (list), `GET /api/search`. A single
`location /api/properties/ { ... }` block (trailing slash) does **not**
match a request to `/api/properties` (no trailing slash) - Nginx's prefix
match is a literal string comparison. Each service in `nginx.conf` gets
two location blocks: an exact match for the bare path and a prefix match
for everything under it.

## Running it locally

Requirements: Docker + Docker Compose. Nothing else - Postgres, Redis, and
Elasticsearch all run in containers, and image uploads default to local
disk storage, so there's no AWS account needed to try it out.

```bash
cp .env.example .env
docker compose up --build
```

Then open:
- **App:** http://localhost:3000
- **API gateway:** http://localhost:8080/api
- **Elasticsearch:** http://localhost:9200

First run takes a minute while Elasticsearch initializes; every service
runs its Django migrations automatically on container start, so there are
no manual migration steps.

### Try the flow end to end
1. Register an account as a **seller** at `/register`.
2. Go to the seller **dashboard → New listing**, add a photo, submit.
   - This fires `PropertyCreated` → Search Service indexes it, Notification
     Service emails the "seller" (logged to console if SMTP isn't configured).
3. Log out, register as a **buyer**, and search for the listing at `/search`.
4. Open the listing and send an inquiry.
   - This fires `InquiryCreated` → Notification Service emails/logs to the
     seller, and it shows up in their dashboard inbox.

## Running a single service without Docker

```bash
cd services/auth-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgres://homescape:homescape@localhost:5432/auth_db
export JWT_ACCESS_SECRET=dev-only-jwt-secret-change-me
export REDIS_URL=redis://localhost:6379/0
python manage.py migrate
python manage.py runserver 0.0.0.0:4001
```

`search-service` and `notification-service` also consume events - run
`python manage.py listen_events` alongside the web server (as its own
process, matching the extra container each gets in `docker-compose.yml`).


## Repo layout

```
homescape/
├── docker-compose.yml
├── .env.example
├── infra/
│   ├── nginx/                  # API Gateway config
│   └── postgres-init/          # creates one DB per service on first boot
├── services/
│   ├── auth-service/
│   ├── property-service/
│   ├── search-service/
│   ├── inquiry-service/
│   ├── media-service/
│   └── notification-service/
└── frontend/
```

Each service follows the same shape: `config/` (Django settings, WSGI
entrypoint), one domain app (e.g. `properties/`) with `models.py`,
`serializers.py`, `views.py`, `urls.py`, and - where relevant -
`events.py` (publish), `events_handlers.py` +
`management/commands/listen_events.py` (subscribe).
