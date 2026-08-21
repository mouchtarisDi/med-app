# AGENTS.md

## Project Overview

This repository contains a university thesis project for a web-based Medical Practice Management System.

The application targets small and medium-sized medical practices and is designed as a multi-tenant SaaS application.

The system includes:

- staff authentication
- clinic management
- role-based authorization
- patient management
- appointment scheduling
- medical records
- payment recording
- notifications
- patient portal using AMKA + OTP
- dashboard and analytics
- intelligent scheduling-related features

The project specification is the main source of truth.

Before making architectural or domain changes, read:

- `docs/system-specification.md`

If the requested task conflicts with the specification, stop and explain the conflict instead of silently changing the architecture.


## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Pydantic

### Frontend

- React
- TypeScript
- Vite

### Infrastructure

- Docker
- Docker Compose

### Version Control

- Git
- GitHub


## Architecture

The backend should follow a layered architecture:

API Layer
→ Service Layer
→ Data Access / ORM Layer
→ PostgreSQL

Keep business logic out of route handlers when possible.

FastAPI routes should mainly handle:

- HTTP input/output
- request validation
- authentication
- authorization
- service invocation

Business rules should live in service-layer code.


## Multi-Tenancy

The application is multi-tenant.

Each medical practice is represented by a Clinic.

Clinic-owned data must remain logically isolated.

Never implement queries that could expose data belonging to another clinic.

Tenant isolation must be considered when implementing:

- patients
- appointments
- medical records
- payments
- users
- doctors
- statistics
- notifications


## Authentication

There are two separate authentication flows.

### Staff

Staff users authenticate using the main authentication system.

Staff roles include:

- OWNER
- DOCTOR
- SECRETARY

A user may have more than one role, for example OWNER + DOCTOR.

Do not design authorization assuming that every user has exactly one role.

### Patients

Patients are not normal application users.

Patients do not have permanent usernames or passwords.

The Patient Portal uses:

AMKA + OTP

Patient authentication must remain separate from staff authentication.

Patient Portal sessions must only expose explicitly allowed patient-facing functionality.


## Patient Portal

Patients may access limited functionality only.

Current intended functionality:

- view upcoming appointments
- cancel eligible appointments
- request or perform rescheduling where permitted

Do not expose medical records through the Patient Portal unless the specification is explicitly changed.


## Payments

Payments are simple internal records.

This project is not an invoicing or accounting system.

A payment may include:

- patient
- appointment
- amount
- payment method
- timestamp
- notes

Payment data is mainly intended for internal statistics.

Do not implement:

- receipts
- invoices
- tax documents
- accounting integrations

unless explicitly requested.


## Intelligent Features

Keep standard automation separate from intelligent features.

### Core automation

Examples:

- appointment conflict detection
- appointment reminders
- follow-up reminders

### Intelligent functionality

Examples:

- no-show risk estimation
- smart appointment availability
- patient alerts

Intelligent features should assist users.

They must not automatically make medical decisions.


## Database Rules

Use SQLAlchemy 2.x conventions already established in the project.

Never change the database schema without an Alembic migration.

When adding or modifying models:

1. inspect existing models and conventions
2. define relationships explicitly
3. consider indexes and constraints
4. create an Alembic migration
5. inspect the generated migration
6. test upgrade and downgrade where practical

Do not manually edit production database state as a substitute for migrations.


## Configuration and Secrets

Do not hardcode:

- passwords
- JWT secrets
- database credentials
- API keys
- OTP provider secrets
- other sensitive configuration

Use environment variables and the project's settings/configuration layer.

Never commit real `.env` files.

Keep `.env.example` updated when new required configuration variables are added.


## Security

This system handles sensitive patient information.

When implementing features, consider:

- authentication
- authorization
- tenant isolation
- input validation
- least privilege
- sensitive-data exposure
- secure error handling
- logging
- rate limiting where appropriate

Do not log:

- passwords
- OTP values
- authentication tokens
- full sensitive medical information

Avoid exposing AMKA unless required by the endpoint.


## Backend Development Rules

Before creating a new backend module, inspect the existing structure and follow established conventions.

Prefer small, focused modules.

Avoid introducing abstractions unless they solve a real current problem.

Do not create large generic frameworks inside the application.

Do not introduce new dependencies unless necessary.

If a new dependency is required:

1. explain why it is needed
2. prefer a well-maintained package
3. add it to the appropriate dependency file
4. mention it in the final task summary


## Frontend Development Rules

Use React + TypeScript.

The project uses Vite.

Frontend environment variables exposed to the browser should follow Vite conventions such as:

`VITE_API_URL`

Do not use Create React App conventions such as `REACT_APP_*` unless the project is intentionally migrated.

Avoid putting authorization rules only in the frontend.

Frontend role checks are for user experience.

Backend authorization remains mandatory.


## Testing

New backend functionality should include tests when practical.

Critical areas should always be tested, especially:

- authentication
- authorization
- tenant isolation
- patient access
- appointment conflicts
- Patient Portal access

Before completing a task, run the relevant tests.

If tests cannot be run, clearly state why.


## Scope Control

Do not modify unrelated files.

Do not refactor unrelated working code unless explicitly requested.

Do not redesign the architecture during a feature task.

If you identify a larger architectural problem:

1. explain it
2. propose a separate task
3. do not silently expand the current task


## Working Style

For non-trivial tasks:

1. inspect relevant code first
2. explain the current behavior
3. propose a short implementation plan
4. implement only the approved/requested scope
5. run relevant tests
6. inspect the final diff
7. summarize the changes and remaining risks

When the prompt explicitly says `do not modify files`, perform analysis only.


## Git

Do not rewrite Git history.

Do not amend existing commits unless explicitly requested.

Keep changes focused enough to form a meaningful commit.

Suggested commit prefixes:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`


## Current Development Priority

The project is currently establishing its foundation.

Before major domain features, prioritize:

1. application configuration
2. Clinic / tenant model
3. User and membership model
4. role-based authorization
5. authenticated current-user handling
6. tenant isolation
7. authentication and authorization tests

After the foundation is stable, proceed with:

1. Patients
2. Appointments
3. Medical Records
4. Payments
5. Patient Portal
6. Notifications
7. Intelligent Features


## Important

Do not attempt to build the entire thesis application in one task.

Prefer small, reviewable changes.

The human developer must remain able to understand and explain the implementation.