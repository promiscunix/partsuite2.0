# PartSuite 2.0 (Django/DRF)

A role-aware portal for parts/service/sales workflows: invoice ingestion, returns/refunds, service radio/VOR tracking, sales due-bill tracking, and notifications. Stack: Django + DRF + Celery + Postgres + Redis. Dev environment is provided via Nix flake.

## Quick start (dev)
1. Install Nix with flakes enabled.
2. Enter the dev shell:
   ```bash
   nix develop
   ```
3. Copy env template and adjust as needed:
   ```bash
   cp .env.example .env
   ```
4. (Optional) Start Postgres/Redis locally or use SQLite for a quick spin (set `DATABASE_URL=sqlite:///db.sqlite3`).
5. Run initial setup:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## What’s scaffolded
- Django project `partsuite` with DRF, custom user model, and Celery wiring.
- Core apps stubbed for: accounts (custom user), suppliers, invoices, receipts, returns, service requests, sales due-bills, notifications, audit, and common utilities.
- Nix dev shell with Python (Django/DRF/Celery stack), Postgres client/server, Redis, MinIO CLI, Tesseract, and PDF tools.
- Server-rendered UI scaffold (Django templates + HTMX) with role-aware navigation, lists, and detail pages for invoices, receipts, returns, service requests, and sales due-bills, plus login/logout views.
- Creation flows and inline actions: create invoices and add lines, log receipt uploads, create return requests, create service requests (radio/VOR) with comments, and create due bills with items and comments. Flash messages are wired in.

## Next implementation steps
- Flesh out API endpoints/serializers/viewsets for each domain.
- Add authentication/authorization policies (DRF auth, role-based permissions, admin seeds).
- Build ingestion flows (invoice upload + parser hooks, CSV receipts import).
- Implement email intake worker and notification jobs.
- Add UI (server-rendered or React) aligned with the domain workflows.

## Testing
- Add pytest + DRF test client in future iterations; none wired yet in this scaffold.

## Operations notes
- Celery broker/backend default to Redis (`CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND`).
- Object storage is not wired yet; PDF paths are modeled as strings for now and can be swapped to MinIO/S3.

## UI usage
- Login at `/login` (create a superuser first). Navigation adapts to the user role.
- Lists/detail views for invoices, receipts, returns, service requests (radio/VOR), and sales due-bills are available under the left nav. These are read-only scaffolds intended to be extended with forms/actions and HTMX endpoints.
- New actions: `Invoices -> New` (plus add lines), `Receipts -> Log receipt`, `Returns -> New return`, `Service -> New request` with comment adds, `Sales -> New due bill` with item and comment adds.
