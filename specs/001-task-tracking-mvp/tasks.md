---

description: "Task list for Student Task Tracking MVP"
---

# Tasks: Student Task Tracking MVP

**Input**: Design documents from `specs/001-task-tracking-mvp/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/api.md`, and `quickstart.md`

**Tests**: Included because the Constitution and specification require tests for
authorization, state transitions, imports, reports, audit behavior, and critical
user journeys.

**Organization**: Tasks are grouped by user story so each story can be implemented
and validated as an independent increment after the foundational phase.

**Implementation status**: This checklist is synchronized with the current
branch. Tasks are checked only when their implementation or automated coverage
is present; manual browser and release-readiness checks remain unchecked.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Python service, responsive web client shell, dependency
management, and local developer commands.

- [X] T001 Create the backend and frontend directory structure from `plan.md` in `backend/app/`, `backend/tests/`, `frontend/templates/`, `frontend/static/`, and `frontend/tests/`.
- [X] T002 Create `pyproject.toml` with Python 3.12 metadata and FastAPI, Pydantic, SQLAlchemy 2, Alembic, Jinja2, HTMX, Argon2id, pytest, and test-client dependencies.
- [X] T003 [P] Add environment configuration and safe defaults in `backend/app/config.py`, `.env.example`, and `backend/app/main.py` without committing secrets.
- [X] T004 [P] Add local development, formatting, linting, and focused-test commands in `Makefile` and `README.md`.
- [X] T005 [P] Create the responsive application shell, navigation placeholders, error surface, and mobile-first base styles in `frontend/templates/base.html`, `frontend/static/css/base.css`, and `frontend/static/js/app.js`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement cross-cutting persistence, authorization, audit, storage,
error handling, and test fixtures. No user story work begins before this phase.

- [X] T006 Create SQLAlchemy base metadata, PostgreSQL session factory, and Alembic configuration in `backend/app/persistence/base.py`, `backend/app/persistence/session.py`, and `backend/alembic.ini`.
- [X] T007 Create the tenant-scoped base repository and query guard in `backend/app/persistence/tenant_scope.py` and `backend/app/persistence/repositories/base.py` so every pedagogical query requires `tenant_id`.
- [X] T008 Create `TeacherAccount`, tenant workspace, and `AuditEvent` mappings with the exact role/status values and nullable tenant rule from `data-model.md` in `backend/app/persistence/models/account.py` and `backend/app/persistence/models/audit.py`.
- [X] T009 Create the initial migration for account, tenant, and audit tables in `backend/migrations/versions/001_initial_schema.py` with normalized email uniqueness and audit indexes.
- [X] T010 Implement secure session extraction, role checks, and teacher/admin authorization dependencies in `backend/app/api/dependencies/auth.py` and `backend/app/services/authorization.py`.
- [X] T011 Implement transaction-scoped audit recording in `backend/app/services/audit_service.py` and `backend/app/persistence/repositories/audit.py`, including actor or automation source, previous values, new values, resource, action, and timestamp.
- [X] T012 Implement the stable error envelope and exception handlers required by `contracts/api.md` in `backend/app/api/errors.py` and `backend/app/main.py`.
- [X] T013 Implement the evidence storage port and local development adapter in `backend/app/storage/ports.py` and `backend/app/storage/local.py`, rejecting ZIP archives before persistence.
- [X] T014 Create pytest fixtures for isolated PostgreSQL transactions, two teacher tenants, an administrator, authenticated clients, academic years, and audit assertions in `backend/tests/conftest.py`.
- [X] T015 [P] Add the foundational API test client and migration smoke test in `backend/tests/conftest.py` and `backend/tests/integration/test_migrations.py`.
- [X] C001 Verify setup and foundation with `pytest backend/tests/integration/test_migrations.py` and the repository lint/type-check commands before starting user stories.

## Phase 3: User Story 1 - Establish a private teacher workspace (Priority: P1)

**Goal**: Teachers can register, authenticate, recover/change passwords, and
administrators can manage account lifecycle without accessing pedagogical data.

**Independent Test**: Create two teachers and an administrator; verify account
flows work, teacher data is isolated, and administrator routes cannot read it.

### Tests for User Story 1

- [X] T016 [P] [US1] Add authentication contract tests for register, login, recovery, password change, and administrator account lifecycle in `backend/tests/contract/test_auth_api.py`.
- [X] T017 [P] [US1] Add cross-tenant and administrator non-disclosure tests in `backend/tests/security/test_tenant_isolation.py`.

### Implementation for User Story 1

- [X] T018 [US1] Implement password hashing, session creation, account status checks, and recovery token rules in `backend/app/services/auth_service.py`.
- [X] T019 [US1] Implement teacher registration, login, recovery, and password endpoints in `backend/app/api/auth_routes.py` using the contract error envelope.
- [X] T020 [US1] Implement administrator teacher create/activate/suspend/deactivate endpoints in `backend/app/api/admin_teacher_routes.py` without pedagogical repository access.
- [X] T021 [US1] Add account lifecycle audit events and security-event audit assertions in `backend/app/services/auth_service.py` and `backend/tests/integration/test_account_audit.py`.
- [X] T022 [US1] Add registration, login, recovery, and inactive-account pages in `frontend/templates/auth/` and connect them through `backend/app/api/page_routes.py`.
- [X] T023 [US1] Add the authenticated workspace shell and authorization-aware navigation in `frontend/templates/workspace.html` and `frontend/static/css/base.css`.
- [X] C002 [US1] Run the US1 contract and security suites and verify two teachers plus an administrator cannot cross the pedagogical boundary; browser smoke and integrated security coverage passed.

## Phase 4: User Story 2 - Set up subjects, sections, and students (Priority: P1)

**Goal**: Teachers create academic years, reusable sections, subjects, students,
and validated CSV/XLSX imports without duplicate or silent invalid data.

**Independent Test**: Create an active year, subject, reusable section, students,
and a mixed-validity import; verify preview errors, duplicate handling, archive
behavior, and academic-year closure.

### Tests for User Story 2

- [X] T024 [P] [US2] Add unit tests for academic-year lifecycle, reusable subject-section relationships, membership transfers, and NIE uniqueness in `backend/tests/unit/test_academic_organization.py`.
- [X] T025 [P] [US2] Add import validation tests for CSV/XLSX mapping, missing fields, malformed rows, duplicate NIE, and critical-error blocking in `backend/tests/unit/test_student_import.py`.
- [X] T026 [P] [US2] Add contract and integration tests for organization routes, active-year scoping, archive behavior, and closure history in `backend/tests/contract/test_organization_api.py` and `backend/tests/integration/test_academic_year.py`.

### Implementation for User Story 2

- [X] T027 [US2] Create academic-year, subject, section, subject-section, student, and membership mappings with the exact fields and uniqueness rules from `data-model.md` in `backend/app/persistence/models/organization.py`.
- [X] T028 [US2] Create the organization migration with one-active-year-per-tenant, tenant-scoped NIE uniqueness, relationship uniqueness, and membership constraints in `backend/migrations/versions/002_academic_organization.py`.
- [X] T029 [US2] Implement academic-year creation/closure, subject/section management, reusable relationships, and archive policies in `backend/app/services/organization_service.py`.
- [X] T030 [US2] Implement manual student creation, section membership, transfer validation, and tenant-scoped NIE lookup in `backend/app/services/student_service.py`.
- [X] T031 [US2] Implement CSV/XLSX preview, normalized row validation, duplicate reporting, import batch persistence, and explicit commit/discard in `backend/app/services/student_import_service.py`.
- [X] T032 [US2] Implement academic organization, student, and import endpoints in `backend/app/api/organization_routes.py` and `backend/app/api/import_routes.py`.
- [X] T033 [US2] Add year, subject, section, student, and import preview pages in `frontend/templates/organization/` with visible validation and empty states.
- [X] T034 [US2] Add audit events for academic-year closure, archival, membership changes, and import commit in `backend/app/services/organization_service.py`, `backend/app/services/student_service.py`, and `backend/app/services/student_import_service.py`.
- [X] C003 [US2] Run the US2 unit, contract, and integration suites and verify the mixed-validity import scenario from `quickstart.md`.

## Phase 5: User Story 3 - Create and review a task roster (Priority: P1)

**Goal**: Teachers create one-section tasks within an academic year and view a
complete student roster with independently tracked deliveries.

**Independent Test**: Create a task for a reusable subject-section relationship
and verify the roster contains exactly the eligible students for that year.

### Tests for User Story 3

- [X] T035 [P] [US3] Add task validation unit and contract tests for subject-section ownership, academic-year scope, required fields, and assignment/due date ordering in `backend/tests/unit/test_task_rules.py` and `backend/tests/contract/test_task_api.py`.
- [X] T036 [P] [US3] Add task and roster contract tests for create, update, archive, and roster retrieval in `backend/tests/contract/test_task_api.py`.
- [X] T037 [P] [US3] Add roster integration tests for membership eligibility, empty sections, archived records, and one delivery per task/student pair in `backend/tests/integration/test_task_roster.py` and `backend/tests/integration/test_mvp_flow.py`.

### Implementation for User Story 3

- [X] T038 [US3] Create task mappings and the one-task/student delivery placeholder constraints in `backend/app/persistence/models/task.py`.
- [X] T039 [US3] Create the task migration with tenant, academic-year, subject-section, date-order, archive, and delivery uniqueness constraints in `backend/migrations/versions/003_tasks.py`.
- [X] T040 [US3] Implement task creation, update, archive, and roster assembly from active section membership in `backend/app/services/task_service.py`.
- [X] T041 [US3] Implement task and roster endpoints in `backend/app/api/task_routes.py` with scoped filters and non-disclosing authorization failures.
- [X] T042 [US3] Add task creation and roster templates with mobile-first state/evidence columns in `frontend/templates/tasks/` and `frontend/static/css/base.css`.
- [X] C004 [US3] Run the US3 suites and verify a task roster on phone and desktop contains the correct students and no cross-tenant rows; Chromium screenshots and teacher-B isolation passed.

## Phase 6: User Story 4 - Record delivery, evidence, and private observations (Priority: P1)

**Goal**: Teachers record delivery states, dates, evidence, and private
observations with automatic due-date transitions and complete audit history.

**Independent Test**: Record on-time and late deliveries, attach allowed evidence,
add multiple observations, run the due-date transition, and inspect the audit log.

### Tests for User Story 4

- [X] T043 [P] [US4] Add state-transition tests for pending, delivered, not-delivered, late, completed, manual correction, date validation, and idempotent automation in `backend/tests/unit/test_delivery_states.py` and `backend/tests/integration/test_delivery_state_matrix.py`.
- [X] T044 [P] [US4] Add evidence and observation validation tests for PDF, Office, image, link, ZIP rejection, private visibility, and multiple observations in `backend/tests/unit/test_evidence_observations.py` and `backend/tests/integration/test_mvp_flow.py`.
- [X] T045 [P] [US4] Add delivery, evidence, observation, and audit contract tests in `backend/tests/contract/test_delivery_api.py` and `backend/tests/integration/test_mvp_flow.py`.
- [X] T046 [P] [US4] Add transaction integration tests proving mutation rollback also rolls back its audit event in `backend/tests/integration/test_delivery_audit.py`.

### Implementation for User Story 4

- [X] T047 [US4] Complete delivery, evidence, and private-observation mappings with allowed kinds and tenant ownership in `backend/app/persistence/models/delivery.py`.
- [X] T048 [US4] Create the delivery/evidence/observation migration with task/student uniqueness and evidence metadata constraints in `backend/migrations/versions/004_delivery_tracking.py`.
- [X] T049 [US4] Implement delivery state transitions, actual-date validation, evidence validation, private observations, and transactional audit orchestration in `backend/app/services/delivery_service.py`.
- [X] T050 [US4] Implement the idempotent due-date worker that transitions overdue pending deliveries and records `automation_source` in `backend/app/workers/due_date_worker.py`.
- [X] T051 [US4] Implement delivery, evidence, and observation endpoints in `backend/app/api/delivery_routes.py` using the storage port and error contract.
- [X] T052 [US4] Add the task-roster editing controls, evidence upload/link UI, observation timeline, and history panel in `frontend/templates/tasks/index.html` and `frontend/static/js/app.js`.
- [X] C005 [US4] Run the US4 suites and verify the complete delivery/evidence/audit scenario from `quickstart.md` across the delivery matrix, evidence/observation flow, due-date worker, rollback audit, and browser smoke coverage.

## Phase 7: User Story 5 - Monitor student and section follow-up (Priority: P2)

**Goal**: Teachers can inspect student profiles, dashboards, Today view, search,
filters, and compliance indicators derived from authoritative deliveries.

**Independent Test**: Seed all delivery states and verify profile, dashboard,
Today, and filtered results reconcile exactly with delivery records.

### Tests for User Story 5

- [X] T053 [P] [US5] Add unit tests for compliance calculations, active/historical-year scope, and dashboard aggregation in `backend/tests/unit/test_follow_up_metrics.py`.
- [X] T054 [P] [US5] Add contract tests for student profile, dashboard, Today, and search/filter endpoints in `backend/tests/contract/test_follow_up_api.py`.
- [X] T055 [P] [US5] Add reconciliation integration tests comparing task rosters, profiles, dashboard counts, and filters in `backend/tests/integration/test_follow_up_reconciliation.py`.

### Implementation for User Story 5

- [X] T056 [US5] Implement scoped profile, dashboard, Today, and search query services in `backend/app/services/follow_up_service.py` without persisted duplicate summary counts.
- [X] T057 [US5] Implement student profile, dashboard, Today, and search endpoints in `backend/app/api/follow_up_routes.py`.
- [X] T058 [US5] Add indexes and query projections for tenant, academic year, section, state, due date, and NIE filters in `backend/migrations/versions/005_follow_up_indexes.py`.
- [X] T059 [US5] Add student profile, dashboard cards, Today view, search controls, and accessible empty/error states in `frontend/templates/follow-up/` and `frontend/static/css/base.css`.
- [X] C006 [US5] Run the US5 suites and reconcile all displayed counts against the seeded delivery dataset.

## Phase 8: User Story 6 - Produce trustworthy reports (Priority: P2)

**Goal**: Teachers generate scoped individual, section, pending-activity, and
compliance reports in print/PDF/Excel/CSV forms without grading data.

**Independent Test**: Generate all four report types from known records and
reconcile each output with the task roster and academic-year scope.

### Tests for User Story 6

- [X] T060 [P] [US6] Add report query and no-grading unit tests for individual, section, pending, compliance, historical scope, and tenant filters in `backend/tests/unit/test_report_queries.py`.
- [X] T061 [P] [US6] Add report contract tests for format selection, print response, export errors, and non-disclosure in `backend/tests/contract/test_report_api.py` and `backend/tests/security/test_tenant_isolation.py`.
- [X] T062 [P] [US6] Add report reconciliation integration tests for all four report types in `backend/tests/integration/test_report_reconciliation.py`.

### Implementation for User Story 6

- [X] T063 [US6] Implement authoritative report query objects and scoped report services in `backend/app/services/report_service.py`.
- [X] T064 [US6] Implement print, PDF, Excel, and applicable CSV renderers behind a report-output port in `backend/app/services/report_outputs.py`.
- [X] T065 [US6] Implement report endpoints with explicit active or historical academic-year scope in `backend/app/api/report_routes.py`.
- [X] T066 [US6] Add report filters, preview, print, and export controls in `frontend/templates/reports/` and `frontend/static/css/base.css`.
- [X] C007 [US6] Run the US6 suites and verify every report reconciles with roster totals and contains no grades, scores, or averages.

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Harden the complete MVP against security, performance, accessibility,
operational, and documentation risks.

- [X] T067 [P] Add CSRF protection, session expiry, rate limits for authentication/import endpoints, safe upload checks, and security regression tests in `backend/app/api/security.py` and `backend/tests/security/`.
- [X] T068 [P] Add performance indexes for rosters and reports in `backend/migrations/versions/006_performance_indexes.py`.
- [X] T069 [P] Add structured request, audit, worker, import, upload, and report logging with correlation identifiers in `backend/app/observability/logging.py`.
- [X] T070 [P] Complete responsive keyboard and screen-reader smoke coverage for the primary flow in `frontend/tests/accessibility/` and `frontend/static/css/`.
- [X] T071 Run the full quickstart scenario and document exact local commands and runtime evidence in `specs/001-task-tracking-mvp/quickstart.md` and `README.md`.
- [X] T072 Review all endpoints and repository methods for tenant predicates, academic-year scope, audit coverage, no-grading leakage, and safe error messages in `backend/tests/security/test_final_review.py`.
- [X] C008 Run the complete test, lint, migration, accessibility, and quickstart gates and record a conditional-go release-readiness result in `specs/001-task-tracking-mvp/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; creates the executable project shell.
- **Foundational (Phase 2)**: Depends on Setup and blocks every user story.
- **User Stories 1-4 (Phases 3-6)**: Depend on Foundation and form the coherent P1 delivery-tracking MVP.
- **User Stories 5-6 (Phases 7-8)**: Depend on delivery records from US4; can proceed in parallel after US4.
- **Polish (Phase 9)**: Depends on all selected stories and checkpoints.

### User Story Dependencies

- **US1**: Depends only on Foundation; establishes authenticated tenant context.
- **US2**: Depends on US1 for authenticated teacher context; can then proceed independently.
- **US3**: Depends on US1 and US2 for teacher, academic year, subject, section, and student membership data.
- **US4**: Depends on US3 for tasks and delivery records.
- **US5**: Depends on US4 for authoritative delivery states and dates.
- **US6**: Depends on US4 for authoritative records and may run in parallel with US5 after US4.

### Parallel Opportunities

- Setup T003-T005 can run in parallel after T001-T002.
- Foundation T012-T015 can run in parallel after T006-T011 where their shared interfaces are stable.
- Within US2, T024-T026 tests can run in parallel; T029-T031 services can be split by file after T027-T028.
- Within US3, T035-T037 tests can run in parallel; T040-T042 can proceed after the task mapping is stable.
- Within US4, T043-T046 tests can run in parallel; T049-T052 can proceed after T047-T048.
- US5 and US6 can run in parallel after US4, with separate service, route, template, and test files.
- Polish T067-T070 can run in parallel after the corresponding interfaces stabilize.

## Parallel Execution Examples

### User Story 2

```text
Task A: T024 academic organization unit tests
Task B: T025 import validation unit tests
Task C: T026 organization contract/integration tests
```

### User Story 4

```text
Task A: T043 delivery state matrix tests
Task B: T044 evidence and observation tests
Task C: T045 delivery API contract tests
Task D: T046 transaction/audit rollback tests
```

### User Stories 5 and 6

```text
Developer A: T053-T059 dashboard, profile, search, and reconciliation
Developer B: T060-T066 report queries, exports, endpoints, and reconciliation
```

## Implementation Strategy

### Coherent MVP Scope

The smallest useful release is US1-US4: private teacher workspace, academic
organization and roster setup, task creation, and delivery/evidence/observation
tracking. US1 alone is the first independently deployable security slice, but it
does not deliver TaskChecker's core value without US2-US4.

### Incremental Delivery

1. Complete Setup and Foundation, then pass C001.
2. Deliver US1 and verify tenant isolation, then pass C002.
3. Deliver US2 and verify import and academic-year lifecycle, then pass C003.
4. Deliver US3 and verify the task roster, then pass C004.
5. Deliver US4 and verify the end-to-end delivery workflow, then pass C005.
6. Add US5 and US6 as reporting/follow-up increments, then pass C006-C007.
7. Complete cross-cutting hardening and C008 before release.

## Format Validation

All implementation tasks use `- [ ] T###`, optional `[P]`, required story labels
for user-story tasks, and at least one concrete repository path. Checkpoints use
the same checkbox and ID convention with `C###` identifiers. No sample task or
template placeholder remains.
