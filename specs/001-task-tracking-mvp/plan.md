# Implementation Plan: Student Task Tracking MVP

**Branch**: `001-task-tracking-mvp` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-task-tracking-mvp/spec.md`

## Summary

Build a mobile-first web application for teacher-owned delivery tracking. The
service will expose validated HTTP contracts, persist authoritative records in
PostgreSQL, keep tenant ownership explicit on every pedagogical query, and use
append-oriented audit events for important changes. A modular FastAPI service
will serve the browser client and JSON endpoints; evidence metadata will live in
PostgreSQL behind a storage adapter so local development and production storage
can differ without changing domain rules.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2, Alembic, Jinja2/HTMX,
Argon2id password hashing, and a storage adapter for evidence files

**Storage**: PostgreSQL for transactional data and audit history; object/file
storage behind an application-owned evidence interface

**Testing**: pytest with unit, API contract, integration, authorization,
state-transition, import, report-reconciliation, and accessibility smoke tests

**Target Platform**: Linux-hosted web service accessed from current mobile,
tablet, and desktop browsers

**Project Type**: Web application with a modular Python service and responsive web client

**Performance Goals**: p95 normal list/task-roster responses under 500 ms for a
teacher workspace with up to 500 active students; import preview of 5,000 rows
under 10 seconds; basic reports under 5 seconds for 10,000 delivery records

**Constraints**: Every pedagogical read and write is tenant-scoped; audit events
are created in the same transaction as important changes; due-date automation is
idempotent; evidence uploads reject ZIP archives; MVP writes require connectivity;
no grades, averages, or student accounts

**Scale/Scope**: Initial target of 50 teachers, 500 students per teacher, 20,000
delivery records per teacher, and one active academic year plus historical years

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Student Data Privacy & Tenant Isolation**: PASS. Tenant ownership is explicit
  in the data model, authorization dependencies are required for every route, and
  administrator routes are limited to account lifecycle data.
- **Traceability First**: PASS. State, date, evidence, observation, archival,
  academic-year, and destructive-action changes emit audit events transactionally.
- **Simple Teacher Workflow**: PASS. The primary task-roster flow is a dedicated
  vertical slice, responsive by default, and measured by the under-30-second user
  criterion.
- **Reliable Data & Reporting**: PASS. PostgreSQL is authoritative; imports are
  previewed; reports query scoped records; reconciliation tests compare reports to
  task rosters.
- **Testable & Maintainable Architecture**: PASS. Domain services are separated
  from HTTP and persistence concerns, with focused unit and integration tests.
- **Product Boundary**: PASS. The design contains delivery compliance indicators
  only and has no grade, score, average, or student-facing account model.

**Post-Phase 1 Re-evaluation**: PASS. The data model, HTTP contract, and
quickstart preserve tenant-scoped ownership, transactional auditability,
academic-year separation, explicit delivery states, mobile-first workflow, and
the no-grading boundary. No constitutional violation or unjustified complexity
was introduced.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-tracking-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── tasks.md              # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/              # HTTP routes, request/response schemas, auth dependencies
│   ├── domain/           # Entities, value rules, state transitions, report policies
│   ├── persistence/      # SQLAlchemy mappings, repositories, migrations integration
│   ├── services/         # Use cases, import validation, audit orchestration
│   ├── workers/          # Idempotent due-date transition job
│   ├── storage/          # Evidence storage port and adapters
│   └── main.py
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    └── security/

frontend/
├── templates/            # Responsive server-rendered pages
├── static/
│   ├── css/
│   └── js/
└── tests/
```

**Structure Decision**: Use one deployable backend with clear domain,
persistence, service, and interface boundaries plus a lightweight responsive
web client. This minimizes deployment complexity for the MVP while preserving
ports for storage and future integrations.

## Complexity Tracking

No constitution violations. The worker, storage port, and audit service are
required boundaries for explicit MVP requirements rather than optional layers.
