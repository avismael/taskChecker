# HTTP Contract: Student Task Tracking MVP

This contract describes the browser-facing service boundary. Exact URL versioning
and schema serialization are implementation details, but the ownership and
behavior rules below are mandatory.

## Cross-Cutting Rules

- Authenticated teacher requests carry the current tenant context.
- Administrator requests may access account lifecycle resources only.
- Unauthorized or cross-tenant resources return the same non-disclosing not-found
  behavior as other inaccessible resources.
- Mutations return the changed resource summary and an audit-event identifier or
  an explicit failure result.
- Validation failures identify fields and actionable correction messages.
- Dates use an unambiguous ISO representation and preserve the stored timezone
  policy selected during implementation.

## Account and Session Resources

### `POST /auth/register`

Creates a teacher registration request or active teacher account according to the
configured account policy.

### `POST /auth/login`

Authenticates a teacher or administrator and establishes an HTTP-only secure
session. The response does not expose password material.

### `POST /auth/recovery` and `POST /auth/password`

Starts password recovery or changes the authenticated teacher's password. Both
flows must avoid account-enumeration leakage and audit the security event.

### `POST /admin/teachers` and `PATCH /admin/teachers/{teacher_id}`

Creates, activates, suspends, or deactivates teacher accounts. These endpoints
must not expose or accept pedagogical records.

## Academic Organization

### `GET|POST /academic-years`

Lists or creates years for the authenticated teacher.

### `POST /academic-years/{year_id}/close`

Closes an active year. The operation is auditable and rejects new active-year
mutations after success.

### `GET|POST|PATCH /subjects`, `/sections`, `/subjects/{id}/sections`

Manages teacher-owned subjects, reusable sections, and their relationships.
Cross-tenant relationship creation is rejected.

### `GET|POST /students`

Creates and searches students in the current tenant and academic scope.

### `POST /students/imports/preview` and `POST /students/imports/{id}/commit`

Previews CSV/XLSX rows with field errors and duplicate findings, then commits
only after explicit confirmation and no critical errors.

## Tasks and Deliveries

### `GET|POST|PATCH /tasks`

Creates and manages tasks scoped to one subject, reusable section, and academic
year. Due-date validation is mandatory.

### `GET /tasks/{task_id}/roster`

Returns each eligible student with delivery state, actual delivery date, evidence
presence, and observation summary. It is the primary classroom workflow.

### `PATCH /tasks/{task_id}/deliveries/{student_id}`

Changes state and/or actual delivery date. The service validates the transition,
records the actor, and writes an audit event transactionally.

### `POST /deliveries/{delivery_id}/evidence`

Adds an allowed evidence item. ZIP archives and unsupported content are rejected.

### `POST /deliveries/{delivery_id}/observations`

Adds a private timestamped observation visible only within the owning tenant.

## Search, Dashboard, and Reports

### `GET /dashboard` and `GET /today`

Return scoped active-year counts and follow-up items. No grade or average fields
are permitted.

### `GET /search`

Supports subject, section, student, task, state, academic-year, and date filters.

### `GET /reports/{individual|section|pending|compliance}`

Generates a scoped report. Export format is selected from print, PDF, Excel, or
applicable CSV. Historical scope must be explicit when requested.

## Error Contract

Errors include a stable machine-readable code, human-readable message, and field
details where applicable. The contract must cover invalid dates, duplicate NIE,
critical import errors, unsupported evidence, archived-year mutations,
unauthorized access, and failed report generation without leaking private data.
