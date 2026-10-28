# backend-sgrh

FastAPI backend for the Human Resources / Human Management System (SGRH).

## Local Setup

Create and activate a Python virtual environment from this repository:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Set at least these variables in `.env` for Supabase PostgreSQL:

```bash
DATABASE_URL=postgresql+psycopg://postgres:password@db.project.supabase.co:5432/postgres
JWT_SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=120
STORAGE_PATH=storage
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=change-this-before-seeding
```

`INITIAL_ADMIN_PASSWORD` is optional. If it is empty, migrations seed roles, permissions, and catalogs only.
If you set it after running migrations, run `python -m app.seed` once to create the initial admin user.

## Migrations

Run backend-owned migrations with Alembic:

```bash
source .venv/bin/activate
python -m alembic upgrade head
```

The first migration creates the SGRH schema and seeds:

- MVP RBAC roles and permissions
- user/status catalogs
- document/file/support-document catalogs
- employee, candidate, contract, affiliation, payroll, offboarding, training, evaluation, and certificate statuses
- payroll novelty catalog
- baseline contract, affiliation, withdrawal, training, and certificate types

## Run

From `backend-sgrh/`, activate the virtual environment and start the ASGI app with uvicorn:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger/OpenAPI:

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

## Start From Scratch

If you are setting up the backend for the first time, use this order:

```bash
cd backend-sgrh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If `INITIAL_ADMIN_PASSWORD` is set in `.env`, run the seed script once after migrations:

```bash
source .venv/bin/activate
python -m app.seed
```

## Tests

Run the endpoint test suite with:

```bash
source .venv/bin/activate
python -m pytest -q
```

The tests use a temporary SQLite database, seed the MVP catalogs/RBAC, create an admin user, and exercise the FastAPI endpoints through `TestClient`.

## Implemented Scope

The backend is a single FastAPI service with module-owned SQLAlchemy models and Pydantic schemas, Alembic migrations, JWT bearer authentication, bcrypt password hashing, RBAC dependencies, audit logging, file upload/download validation, and routers for:

- auth and admin users/RBAC
- employees
- recruitment, candidates, interviews, tests, verifications, occupational exams, and contracts
- affiliations
- payroll periods, novelties, settlements, pay slips, reports, and contributions exports
- offboarding and contract settlement approval
- training activities, attendance, and annual plans
- performance evaluations and improvement plans
- employment certificates
- documents
- reports
- audit

Generated PDFs/exports are practical MVP stubs stored as `documento` records so the storage/linking model is ready for later full PDF/Excel rendering.

## Project Structure

Each domain module owns its API router, ORM models, and DTO schemas:

```text
app/
  core/                 # config, db, security, RBAC, shared model mixins
  modules/
    auth/
    employees/
    recruitment/
    affiliations/
    payroll/
    offboarding/
    training/
    evaluations/
    certificates/
    documents/
    reports/
    audit/
```

`app.models` and `app.schemas` are compatibility import surfaces only. New code should import from the owning module, for example `app.modules.employees.models` or `app.modules.payroll.schemas`.
