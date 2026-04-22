# AgnaYI Real Estate CRM

Production-grade Real Estate CRM with Django/React/Postgres/Redis/Docker.

## Status
- [x] Phase 1 Planning (schema)
- [x] Phase 2 Core: Auth + Module 1 Leads (FULL backend/frontend)
- [ ] Phase 2+ Properties, Clients, Deals...
- Full completion in progress.

## Quick Start
1. Backend:
```bash
docker compose up -d db backend
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```
API Docs: http://localhost:8000/api/docs/

2. Frontend:
```bash
cd frontend
npm install  # Retry if failed
npm run dev
```
http://localhost:3000

## Test Leads
- Login admin@test.com / pass (backend shell python manage.py shell create users)
- /leads table, create/update/status

Full features coming...

