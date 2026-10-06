# Graph Report - taskChecker  (2026-10-02)

## Corpus Check
- 145 files · ~61,080 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 7, .csv 2, .example 1)

## Summary
- 971 nodes · 2181 edges · 63 communities (36 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 172 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5107b162`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- seed.py
- auth_routes.py
- organization_routes.py
- security.py
- add_file_evidence
- common.sh
- test_report_queries.py
- app.js
- Tasks: Student Task Tracking MVP
- tenant_scope.py
- page_routes.py
- User Scenarios & Testing *(mandatory)*
- HTTP Contract: Student Task Tracking MVP
- graphify.js
- opencode.json
- app/__init__.py
- observability/__init__.py
- services/__init__.py
- storage/__init__.py
- workers/__init__.py
- backend/__init__.py
- taskchecker
- Tasks: [FEATURE NAME]
- speckit.analyze.md
- tenant_id
- Execution Steps
- Feature Specification: [FEATURE NAME]
- Task List
- speckit.plan.md
- speckit.specify.md
- speckit.tasks.md
- Core Principles
- Core Principles
- Implementation Plan: [FEATURE]
- speckit.checklist.md
- Research: Student Task Tracking MVP
- speckit.clarify.md
- speckit.implement.md
- Skill Registry — taskChecker
- Ejemplos de importación de estudiantes
- speckit.constitution.md
- TaskChecker
- speckit.taskstoissues.md
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- env.py
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `get_db()` - 45 edges
2. `CurrentActor` - 43 edges
3. `require_teacher()` - 39 edges
4. `Base` - 38 edges
5. `DeliveryStatus` - 27 edges
6. `audit()` - 27 edges
7. `TeacherAccount` - 25 edges
8. `Student` - 23 edges
9. `AcademicYear` - 21 edges
10. `get_settings()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Phase 2: Foundational (Blocking Prerequisites)` --references--> `TeacherAccount`  [INFERRED]
  specs/001-task-tracking-mvp/tasks.md → backend/app/persistence/models/account.py
- `Phase 2: Foundational (Blocking Prerequisites)` --references--> `AuditEvent`  [INFERRED]
  specs/001-task-tracking-mvp/tasks.md → backend/app/persistence/models/audit.py
- `Academic Year` --references--> `tenant_id()`  [INFERRED]
  specs/001-task-tracking-mvp/data-model.md → backend/tests/conftest.py
- `Audit Event` --references--> `tenant_id()`  [INFERRED]
  specs/001-task-tracking-mvp/data-model.md → backend/tests/conftest.py
- `Delivery` --references--> `tenant_id()`  [INFERRED]
  specs/001-task-tracking-mvp/data-model.md → backend/tests/conftest.py

## Import Cycles
- None detected.

## Communities (63 total, 27 thin omitted)

### Community 0 - "seed.py"
Cohesion: 0.05
Nodes (108): Base, TimestampMixin, AuditEvent, Delivery, DeliveryStatus, Evidence, PrivateObservation, StrEnum (+100 more)

### Community 1 - "auth_routes.py"
Cohesion: 0.07
Nodes (56): Any, argon2, argon2_exceptions, create_teacher(), BaseModel, Depends, patch, post (+48 more)

### Community 3 - "organization_routes.py"
Cohesion: 0.07
Nodes (93): DeliveryPayload, evidence_file(), evidence_link(), history(), LinkPayload, observation(), ObservationPayload, BaseModel (+85 more)

### Community 4 - "security.py"
Cohesion: 0.15
Nodes (14): anyio, CSRFMiddleware, enforce_rate_limit(), BaseHTTPMiddleware, Request, test_rate_limit_rejects_after_limit(), test_rate_limit_uses_separate_keys(), test_upload_limit_rejects_oversized_content() (+6 more)

### Community 5 - "add_file_evidence"
Cohesion: 0.07
Nodes (24): add_file_evidence(), add_link_evidence(), add_observation(), delivery_history(), Session, UUID, _tenant_delivery(), LocalEvidenceStorage (+16 more)

### Community 6 - "common.sh"
Cohesion: 0.12
Nodes (28): check-prerequisites.sh script, check_dir(), check_file(), find_specify_root(), format_speckit_command(), get_current_branch(), get_feature_paths(), get_invoke_separator() (+20 more)

### Community 7 - "test_report_queries.py"
Cohesion: 0.08
Nodes (29): CorrelationMiddleware, log_event(), BaseHTTPMiddleware, Request, DefaultReportOutput, Protocol, ReportOutputPort, csv_bytes() (+21 more)

### Community 8 - "app.js"
Cohesion: 0.08
Nodes (29): extractErrorMessage(), followUpYear, formatDeliveryDate(), importForm, loginForm, logoutButton, nativeFetch, recoveryForm (+21 more)

### Community 9 - "Tasks: Student Task Tracking MVP"
Cohesion: 0.06
Nodes (34): Coherent MVP Scope, Dependencies & Execution Order, Format Validation, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation for User Story 4, Implementation for User Story 5 (+26 more)

### Community 11 - "page_routes.py"
Cohesion: 0.33
Nodes (17): _account_role_label(), follow_up_page(), home(), inactive_account_page(), login_page(), organization_page(), get, Request (+9 more)

### Community 13 - "User Scenarios & Testing *(mandatory)*"
Cohesion: 0.06
Nodes (30): Content Quality, Feature Readiness, Notes, Requirement Completeness, Specification Quality Checklist: Student Task Tracking MVP, Complexity Tracking, Constitution Check, Documentation (this feature) (+22 more)

### Community 14 - "HTTP Contract: Student Task Tracking MVP"
Cohesion: 0.06
Nodes (31): Academic Organization, Account and Session Resources, Cross-Cutting Rules, Error Contract, `GET /dashboard` and `GET /today`, `GET|POST /academic-years`, `GET|POST|PATCH /subjects`, `/sections`, `/subjects/{id}/sections`, `GET|POST|PATCH /tasks` (+23 more)

### Community 16 - "graphify.js"
Cohesion: 0.40
Nodes (3): IMPORTANT: keep the reminder string free of backticks and $(...) constructs., ref_fs, ref_path

### Community 36 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 37 - "speckit.analyze.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 39 - "tenant_id"
Cohesion: 0.09
Nodes (30): install_error_handlers(), FastAPI, reset_rate_limits(), create_app(), lifespan(), FastAPI, client(), tenant_id() (+22 more)

### Community 40 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 41 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 42 - "Task List"
Cohesion: 0.15
Nodes (12): Architecture Decisions, Checkpoint: Delivery Coverage, Checkpoint: Foundation Coverage, Checkpoint: MVP Coverage, Implementation Plan: Complete Pending MVP Coverage, Open Questions, Overview, Phase 1: Authentication and Organization Coverage (+4 more)

### Community 43 - "speckit.plan.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 44 - "speckit.specify.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, For AI Generation, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements (+2 more)

### Community 45 - "speckit.tasks.md"
Cohesion: 0.18
Nodes (10): Checklist Format (REQUIRED), Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules (+2 more)

### Community 46 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Development Workflow and Quality Gates, Governance, I. Student Data Privacy & Tenant Isolation, II. Traceability First, III. Simple Teacher Workflow, IV. Reliable Data & Reporting, Product Boundary and Domain Constraints (+2 more)

### Community 47 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 48 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 49 - "speckit.checklist.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 50 - "Research: Student Task Tracking MVP"
Cohesion: 0.25
Nodes (7): Decision: FastAPI with dependency-based authorization, Decision: PostgreSQL as source of truth and evidence storage port, Decision: pytest with layered fixtures and parametrized domain tests, Decision: Server-rendered responsive client with progressive enhancement, Decision: SQLAlchemy 2 ORM with explicit transaction boundaries, Research: Student Task Tracking MVP, Resolved Planning Unknowns

### Community 51 - "speckit.clarify.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 52 - "speckit.implement.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 53 - "Skill Registry — taskChecker"
Cohesion: 0.33
Nodes (5): Contract, Loading protocol, Skill Registry — taskChecker, Skills, Sources scanned

### Community 54 - "Ejemplos de importación de estudiantes"
Cohesion: 0.33
Nodes (5): Archivos, Ejemplos de importación de estudiantes, Encabezados aceptados, Uso desde la interfaz, Uso mediante API

### Community 55 - "speckit.constitution.md"
Cohesion: 0.33
Nodes (5): Outline, Post-Execution Checks, Pre-Execution Checks, Scope Guard, User Input

### Community 56 - "TaskChecker"
Cohesion: 0.33
Nodes (5): Datos de desarrollo, Desarrollo, Docker, TaskChecker, Verificación

### Community 58 - "speckit.taskstoissues.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 59 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 60 - "env.py"
Cohesion: 0.09
Nodes (11): alembic, alembic_config, downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade() (+3 more)

## Knowledge Gaps
- **271 isolated node(s):** `$schema`, `plugin`, `common.sh script`, `nativeFetch`, `workspaceMetrics` (+266 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 448 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Phase 2: Foundational (Blocking Prerequisites)` connect `Tasks: Student Task Tracking MVP` to `seed.py`, `auth_routes.py`, `tenant_id`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `TeacherAccount` connect `auth_routes.py` to `seed.py`, `Tasks: Student Task Tracking MVP`, `organization_routes.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `CurrentActor` (e.g. with `update_teacher()` and `evidence_file()`) actually correct?**
  _`CurrentActor` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Base` (e.g. with `lifespan()` and `downgrade()`) actually correct?**
  _`Base` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `common.sh script` to the rest of the system?**
  _271 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `seed.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05259529203191175 - nodes in this community are weakly interconnected._
- **Should `auth_routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07003129890453834 - nodes in this community are weakly interconnected._