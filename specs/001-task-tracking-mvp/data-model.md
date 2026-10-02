# Data Model: Student Task Tracking MVP

## Ownership Rule

Every pedagogical entity carries `tenant_id`, which identifies the owning
teacher workspace. All repository methods require the authenticated actor's
tenant context. Administrator records are separate from pedagogical ownership;
administrator account lifecycle operations never receive a pedagogical tenant
query path.

## Entities

### Teacher Account

- `id`: stable identifier
- `email`: normalized unique login identifier
- `password_hash`: Argon2id password hash
- `role`: `teacher` or `administrator`
- `status`: pending, active, suspended, or deactivated
- `created_at`, `updated_at`

Teachers own one tenant workspace. Administrators may manage account status but
have no authorization to read or mutate pedagogical records.

### Academic Year

- `id`, `tenant_id`
- `label`: teacher-visible period label
- `status`: active or closed
- `starts_on`, `ends_on`
- `closed_at`, `created_at`

Only one active year is permitted per tenant. Closing a year is auditable and
prevents new active-year mutations while retaining historical reads.

### Subject

- `id`, `tenant_id`, `name`, `description`
- `archived_at`, `created_at`, `updated_at`

Subjects relate to reusable sections through `subject_sections`.

### Section

- `id`, `tenant_id`, `name`
- `archived_at`, `created_at`, `updated_at`

Sections are teacher-owned groups reusable across multiple subjects. They are
not duplicated when a subject relationship is added.

### Subject Section

- `subject_id`, `section_id`
- `tenant_id`, `created_at`

The compound key prevents duplicate relationships. Both referenced entities must
belong to the same tenant.

### Student

- `id`, `tenant_id`
- `nie`: normalized unique identifier within tenant
- `first_name`, `last_name`
- `archived_at`, `created_at`, `updated_at`

NIE uniqueness is tenant-scoped. Student identity is independent from subject;
section membership provides the academic grouping.

### Student Section Membership

- `id`, `tenant_id`, `student_id`, `section_id`, `academic_year_id`
- `joined_on`, `left_on`
- `status`: active or ended

This relationship preserves transfers and historical section context without
duplicating students. Only one active membership per student and academic year
is allowed in the MVP.

### Task

- `id`, `tenant_id`, `academic_year_id`
- `subject_id`, `section_id`
- `title`, `description`, `instructions`
- `assigned_on`, `due_on`
- optional `attachment_ref`, `link`, `internal_notes`
- `archived_at`, `created_at`, `updated_at`

The subject and section relationship must exist in the same tenant. `due_on`
cannot precede `assigned_on`. MVP targeting is one complete section.

### Delivery

- `id`, `tenant_id`, `task_id`, `student_id`
- `status`: pending, delivered, not_delivered, late, completed
- `actual_delivered_at`
- `created_at`, `updated_at`

There is one delivery per task/student pair. The student must have an active or
historical membership in the task's section for the task's academic year.

### Evidence

- `id`, `tenant_id`, `delivery_id`
- `kind`: pdf, office_document, image, or link
- `original_name`, `content_type`, `size_bytes`
- `storage_ref` or `url`
- `created_at`

ZIP archives and unsupported types are rejected before persistence. Evidence is
owned through the delivery and therefore inherits tenant isolation.

### Private Observation

- `id`, `tenant_id`, `delivery_id`, `author_teacher_id`
- `body`, `created_at`

Observations are append-only for normal use and visible only to the owning
teacher workspace.

### Import Batch and Import Row

- Batch: `id`, `tenant_id`, `academic_year_id`, `source_name`, `status`, timestamps
- Row: `batch_id`, row number, normalized values, validation errors, action

The preview persists validation results until the teacher confirms or discards
the batch. Critical errors block confirmation. Existing or repeated NIE values
are reported and never merged automatically.

### Audit Event

- `id`, `tenant_id` nullable only for account-lifecycle events
- `actor_account_id` or `automation_source`
- `resource_type`, `resource_id`, `action`
- `previous_values`, `new_values`, `reason`
- `occurred_at`

Audit events are append-oriented, tenant-protected, and written in the same
transaction as the mutation they describe. Account lifecycle events are visible
only to authorized administrators and the affected teacher as appropriate.

## State Rules

| Current | Trigger | Next | Source |
|---|---|---|---|
| pending | Teacher records on-time delivery | delivered | teacher |
| pending | Due date passes without delivery | not_delivered | automation |
| not_delivered | Teacher records delivery after due date | late | teacher |
| delivered | Teacher confirms follow-up complete | completed | teacher |
| late | Teacher confirms follow-up complete | completed | teacher |
| any valid state | Authorized correction | selected valid state | teacher |

Every transition is validated, idempotent where automated, and audited.

## Derived Reporting Rules

- Compliance is a delivery-follow-up indicator, not a grade.
- Active reports exclude closed academic years unless explicitly requested as
  historical scope.
- Counts are derived from deliveries, not duplicated summary fields.
- Report queries must carry tenant and academic-year scope.
