# Research: Student Task Tracking MVP

## Decision: FastAPI with dependency-based authorization

**Rationale**: FastAPI provides typed request validation, dependency injection,
and security-scope patterns suitable for enforcing teacher and administrator
permissions at every route. The framework's documented background-task facility
is sufficient for non-critical follow-up work, while due-date state changes will
use a separate idempotent worker boundary because state transitions and audit
events are business-critical.

**Alternatives considered**: Flask was not selected because the MVP needs more
explicit request schemas and dependency-driven authorization from the start.
Django was not selected because the project currently has no need for its larger
opinionated application surface.

**Sources**: FastAPI security scopes and dependency documentation; FastAPI
background task reference, retrieved through Context7 from the official FastAPI
documentation.

## Decision: SQLAlchemy 2 ORM with explicit transaction boundaries

**Rationale**: SQLAlchemy 2 supports typed relationships, explicit sessions, and
transaction framing that can commit a domain mutation and its audit event as one
unit. Repository/query boundaries will keep tenant filters visible and testable.
Alembic will manage schema evolution.

**Alternatives considered**: Direct SQL was rejected for the MVP because the
number of related entities and lifecycle rules would make repeated mapping and
transaction code harder to maintain. A framework-specific ORM was not chosen
because FastAPI does not require one and SQLAlchemy keeps persistence portable.

**Sources**: SQLAlchemy 2 ORM quickstart, relationship, and session transaction
documentation from the official SQLAlchemy documentation.

## Decision: pytest with layered fixtures and parametrized domain tests

**Rationale**: Fixtures can provide isolated tenant, academic-year, database,
and authenticated-client contexts. Parametrization fits the delivery state
transition matrix, import validation cases, and authorization permutations.

**Alternatives considered**: The standard-library unittest framework would work,
but pytest offers clearer fixture composition and test discovery for this domain.

**Sources**: pytest fixture and parametrization documentation from the official
pytest documentation.

## Decision: Server-rendered responsive client with progressive enhancement

**Rationale**: A server-rendered client with small targeted interactions keeps the
MVP deployment simple, supports mobile-first pages quickly, and avoids creating a
second API consumer before the domain contracts stabilize. The HTTP contract is
still documented so a richer client or integrations can be added later.

**Alternatives considered**: A separate SPA would provide richer client state,
but would add an independent build, authentication surface, and duplicated
validation before offline synchronization is in scope.

## Decision: PostgreSQL as source of truth and evidence storage port

**Rationale**: Transactional relational storage fits teacher ownership, academic
years, reusable sections, deliveries, reporting joins, and audit history. Files
will be addressed through a storage port; local development may use filesystem
storage while deployment can use object storage without changing the domain.
ZIP archives are rejected before storage.

**Alternatives considered**: Storing evidence blobs directly in PostgreSQL was
not selected for the MVP because it couples database growth to file size and
serving concerns. A provider-specific storage SDK is deferred behind the port.

## Resolved Planning Unknowns

- Framework: FastAPI.
- Persistence mapping: SQLAlchemy 2 with Alembic.
- Test framework: pytest.
- Target: Linux web service with responsive browser client.
- Initial scale and response targets: recorded in `plan.md` and treated as
  planning assumptions to validate during implementation.
- Offline synchronization, external integrations, grading, and student accounts:
  explicitly outside the MVP.
