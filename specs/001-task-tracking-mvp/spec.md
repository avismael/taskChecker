# Feature Specification: Student Task Tracking MVP

**Feature Branch**: `001-task-tracking-mvp`

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: TaskChecker MVP for multi-teacher student task delivery tracking, evidence, private observations, reporting, and audit history.

## Clarifications

### Session 2026-10-02

- Q: How should teacher accounts be created and administered? → A: Teachers may self-register, and an administrator may manage account lifecycle without accessing pedagogical data.
- Q: Should a section belong to one subject or relate to multiple subjects? → A: A teacher-owned section may relate to multiple subjects, and students are registered once rather than duplicated per subject.
- Q: Should the system change delivery states automatically when the due date passes? → A: At the due date, Pendiente becomes No entregada; a later delivery becomes Entrega tardía; teachers may correct states manually.
- Q: Which evidence types should the MVP accept? → A: PDF, Office documents, images, and links; ZIP archives are excluded from the MVP.
- Q: Should the MVP explicitly manage academic years to separate and preserve history? → A: Each period has an academic year; closing it preserves its data separately from active records.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Establish a private teacher workspace (Priority: P1)

A teacher creates an account or is activated by an administrator, signs in, and manages a private workspace containing only their students, subjects, sections, tasks, evidence, observations, and reports. An administrator may create, activate, or deactivate teacher accounts but cannot access pedagogical data.

**Why this priority**: Privacy and tenant isolation are prerequisites for every other workflow.

**Independent Test**: Create two teacher accounts, add data to each, and verify that neither account can discover or access the other's data.

**Acceptance Scenarios**:

1. **Given** a new teacher, **When** they self-register or an administrator activates their account and they sign in, **Then** they can access their own empty workspace.
2. **Given** an administrator manages a teacher account, **When** the administrator searches for students, tasks, evidence, observations, or reports, **Then** pedagogical records are not accessible.
3. **Given** two teachers with separate records, **When** either teacher searches, filters, or opens a report, **Then** only that teacher's records are returned.
4. **Given** a teacher is not authorized for a record, **When** they attempt to open it directly, **Then** access is denied without revealing its contents.

---

### User Story 2 - Set up subjects, sections, and students (Priority: P1)

A teacher creates or opens an academic year, creates subjects and reusable sections, associates sections with subjects, and registers students manually or through CSV/XLSX import, previews validation results, and corrects critical errors before data is saved.

**Why this priority**: A reliable roster is required before tasks can be assigned or tracked.

**Independent Test**: Create a subject and section, add a student manually, import a mixed-validity file, and verify valid records and validation feedback.

**Acceptance Scenarios**:

1. **Given** an active subject, **When** the teacher creates or reuses a section and adds a student with NIE, first name, and last name, **Then** the section is associated with the subject and the student appears once in that section.
2. **Given** an import containing valid rows, missing NIE, missing name, malformed rows, and duplicate NIE values, **When** the teacher previews it, **Then** each issue is identified before import and critical errors prevent silent completion.
3. **Given** an imported student with an existing NIE in the teacher's workspace, **When** the import is validated, **Then** the duplicate is reported and no second student is created.
4. **Given** an archived subject, section, or student with history, **When** the teacher views archived records, **Then** historical associations remain available and are not mixed into active lists.
5. **Given** an academic year with historical records, **When** the teacher closes it and starts working in a new year, **Then** the closed year's records remain available separately and are not included in active-year counts.

---

### User Story 3 - Create and review a task roster (Priority: P1)

A teacher creates a task for a subject and section, opens it, and sees every associated student with the current delivery state, due date, evidence indicator, and observation context.

**Why this priority**: The task roster is the primary classroom workflow and the core product value.

**Independent Test**: Create a task for a populated section and verify that the roster contains exactly that section's students and the task's required dates.

**Acceptance Scenarios**:

1. **Given** a section with students, **When** the teacher creates a task with title, description, assignment date, and due date, **Then** the task is associated with the selected subject and section.
2. **Given** an assigned task, **When** the teacher opens it, **Then** the roster lists all associated students with independent delivery records.
3. **Given** a task without evidence, **When** the teacher views it, **Then** the task remains valid and clearly indicates that no evidence is attached.

---

### User Story 4 - Record delivery, evidence, and private observations (Priority: P1)

A teacher quickly updates a student's delivery state, records the actual delivery date, attaches evidence, and adds one or more private observations while preserving the complete history.

**Why this priority**: This is the daily action that keeps follow-up data trustworthy.

**Independent Test**: Change a student's state from pending to delivered, add an on-time or late date, attach evidence, add two observations, and verify the resulting timeline.

**Acceptance Scenarios**:

1. **Given** a pending delivery, **When** the teacher records an actual delivery date on or before the due date, **Then** the delivery can be marked Entregada and the date is retained.
2. **Given** a delivery after the due date, **When** the teacher records the actual date, **Then** the record can be marked Entrega tardía and the late date remains visible.
3. **Given** a delivery record, **When** the teacher attaches a file, document, image, or link, **Then** the evidence is associated with that student and task.
4. **Given** an existing delivery record, **When** the teacher adds multiple observations, **Then** each observation retains its text, date, and time and is visible only to its owner.
5. **Given** any important change, **When** it is saved, **Then** the history records the actor, timestamp, action, previous value where applicable, and new value where applicable.

---

### User Story 5 - Monitor student and section follow-up (Priority: P2)

A teacher views a student profile, dashboard, daily view, or filtered task list to identify pending, overdue, late, and completed work without treating compliance as an academic grade.

**Why this priority**: Fast follow-up turns recorded delivery data into useful classroom action.

**Independent Test**: Seed records across all states, open the dashboard and a student profile, and verify that counts, filters, and completion percentages agree with the underlying records.

**Acceptance Scenarios**:

1. **Given** a student with tasks in multiple states, **When** the teacher opens the profile, **Then** the profile shows tasks, dates, evidence, observations, history, state counts, and a clearly labeled compliance percentage.
2. **Given** tasks across sections and dates, **When** the teacher filters by subject, section, student, task, state, or date, **Then** results include only matching records in the teacher's workspace.
3. **Given** the current date, **When** the teacher opens Today, **Then** tasks due today, deliveries recorded today, pending students, and follow-up tasks are highlighted.
4. **Given** any compliance percentage, **When** it is displayed, **Then** it is labeled as delivery follow-up and never presented as a grade, score, or average.

---

### User Story 6 - Produce trustworthy reports (Priority: P2)

A teacher generates individual, section, pending-activity, and compliance reports for their own data and prints or exports them without losing scope or status meaning.

**Why this priority**: Reports provide durable evidence for follow-up while preserving the product boundary.

**Independent Test**: Generate all four report types from known records and compare their totals, filters, and statuses against the task rosters.

**Acceptance Scenarios**:

1. **Given** a student with historical delivery records, **When** the teacher generates an individual report, **Then** it includes the student's tasks, states, dates, evidence references, observations, and history.
2. **Given** a section, **When** the teacher generates a section or pending-activity report, **Then** the report includes only that section's students and selected reporting scope.
3. **Given** a report, **When** the teacher prints or exports it, **Then** the output preserves labels, dates, scope, and delivery indicators without adding grades.

---

### Edge Cases

- A task due date cannot precede its assignment date.
- An actual delivery date cannot precede the task assignment date; a date after the due date is explicitly late.
- A task with no students or an archived section remains visible with a clear empty or historical state and does not create misleading compliance totals.
- Archiving a student, section, subject, or task preserves historical records and removes it from active selection lists.
- Closing an academic year preserves its students, tasks, evidence, observations, reports, and history while excluding them from active-year workflows.
- Changing a due date, moving a student, deleting a task with history, or changing a state creates an auditable event and never silently destroys history.
- Invalid or unsupported evidence, including ZIP archives, is rejected with a visible reason; a task may remain without evidence.
- Temporary loss of connectivity is documented as a future capability and is not required for MVP completion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a teacher to self-register or be activated by an administrator, authenticate, and access only their own workspace; administrators MUST be limited to teacher-account lifecycle management and MUST NOT access pedagogical data.
- **FR-002**: The system MUST enforce tenant isolation for students, subjects, sections, tasks, deliveries, evidence, observations, reports, and history.
- **FR-003**: The system MUST allow a teacher to create, edit, archive, and later consult subjects and reusable sections, and MUST allow a section to relate to multiple subjects.
- **FR-004**: The system MUST allow a teacher to create and close academic years, preserve closed-year records, and exclude them from active-year workflows and counts.
- **FR-005**: The system MUST allow a teacher to create students manually with a unique NIE, first name, last name, and section association without duplicating the student when the section is related to additional subjects.
- **FR-006**: The system MUST support CSV and XLSX student imports with preview, row-level validation, duplicate detection, and visible critical-error handling before persistence.
- **FR-007**: The system MUST allow a teacher to create a task with title, description, subject, section, academic year, assignment date, and due date, plus optional instructions, attachment, link, and internal notes.
- **FR-008**: The system MUST create an independent delivery record for each student associated with a task.
- **FR-009**: The system MUST support the states Pendiente, Entregada, No entregada, Entrega tardía, and Completada with the meanings defined in the user scenarios.
- **FR-010**: The system MUST automatically transition a pending delivery to No entregada when its due date passes without a recorded delivery, MUST classify a later delivery as Entrega tardía, and MUST allow the teacher to correct states manually.
- **FR-011**: The system MUST allow manual state changes and MUST record previous state, new state, actor or automation source, date, and time for each change.
- **FR-012**: The system MUST store assignment date, due date, and actual delivery date independently and preserve them after later state changes.
- **FR-013**: The system MUST distinguish on-time from late delivery using the actual delivery date and due date.
- **FR-014**: The system MUST associate zero or more evidence items with a student-task delivery, including PDF files, common Office documents, images, and links, and MUST reject ZIP archives in the MVP.
- **FR-015**: The system MUST allow multiple private observations per delivery, each with text, date, and time, visible only to the owning teacher.
- **FR-016**: The system MUST show a task roster containing students, state, actual delivery date, evidence presence, and observation context, with rapid state editing.
- **FR-017**: The system MUST provide student profiles with identity, section, related subjects, task totals, state counts, compliance percentage, evidence, observations, and history.
- **FR-018**: The system MUST provide dashboard and Today views for active work, due work, pending and late work, recent deliveries, section compliance, and follow-up students.
- **FR-019**: The system MUST provide search and filters by subject, section, student, task, state, academic year, and date.
- **FR-020**: The system MUST provide individual, section, pending-activity, and compliance reports with print, PDF, Excel, and applicable CSV output.
- **FR-021**: Reports and compliance indicators MUST describe delivery follow-up only and MUST NOT calculate or display grades, scores, or academic averages.
- **FR-022**: The system MUST record important actions including state changes, deliveries, actual-date changes, evidence additions, observations, academic-year closure, archival, and destructive-action attempts.
- **FR-023**: The system MUST recommend archiving for records with history and MUST require explicit confirmation before permanent deletion; deletion MUST NOT silently destroy required historical records.
- **FR-024**: The primary task-roster flow MUST be usable on phones, tablets, and computers, and MUST support keyboard navigation, readable labels, and clear feedback for errors and saved changes.
- **FR-025**: The system MUST preserve a boundary for future multi-section and individual assignment, external integrations, and limited-connectivity synchronization without requiring those capabilities in the MVP.

### Key Entities *(include if feature involves data)*

- **Teacher**: The authenticated owner of a private workspace and its records.
- **Academic Year**: A teacher-owned period that scopes active records and can be closed while preserving historical data.
- **Subject**: A teacher-owned academic area related to one or more reusable sections.
- **Section**: A teacher-owned group containing students and assigned tasks that may be related to multiple subjects.
- **Student**: A teacher-owned learner identified by a unique NIE within the workspace.
- **Task**: A delivery-tracking activity associated with a subject and section, with assignment and due dates.
- **Delivery**: The student-specific record for a task, including state and actual delivery date.
- **Evidence**: A file, document, image, or link attached to a delivery.
- **Private Observation**: A timestamped teacher-only note associated with a delivery.
- **Audit Event**: An immutable or append-oriented record of an important action, actor, time, resource, and relevant value changes.
- **Report**: A scoped representation of authoritative delivery records for a student, section, pending work, or compliance follow-up.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teacher can complete the primary setup-to-follow-up journey from account access through a basic report in no more than 16 deliberate workflow steps.
- **SC-002**: In usability testing, at least 90% of teachers can open a section task, find a named student, and change the delivery state in under 30 seconds on a phone.
- **SC-003**: At least 95% of valid imported student rows are previewed with correct field mapping and validation outcome before persistence.
- **SC-004**: 100% of cross-teacher access attempts in authorization tests are denied without exposing the target record.
- **SC-005**: 100% of tested state changes, delivery dates, evidence additions, observations, archival actions, and report scopes have attributable history or visible failure feedback.
- **SC-006**: For a known dataset, dashboard counts, student profiles, task rosters, and all four report types agree on delivery totals and states in 100% of reconciliation tests.
- **SC-007**: At least 90% of representative teachers can answer what was due, the current delivery state, and what evidence or history exists without assistance.
- **SC-008**: No MVP acceptance test creates or displays grades, scores, averages, or student-facing access.

## Assumptions

- Teachers may self-register or be created, activated, and deactivated by an administrator; administrators manage account lifecycle only and cannot access pedagogical data. Standard email-and-password authentication, password recovery, and password change are assumed.
- NIE is unique within each teacher workspace for MVP; cross-teacher identity matching is out of scope.
- A duplicate import row is rejected or reported rather than merged automatically.
- A task is initially assigned to one complete section within one subject and academic year; multi-section and individual targeting are reserved for a later increment.
- The system automatically applies due-date transitions and the teacher may correct any resulting state manually; automated and manual changes are both auditable.
- Archiving is the normal lifecycle operation. Permanent deletion is restricted to records whose historical dependencies permit safe removal.
- Compliance percentage is a descriptive delivery indicator based on completed activities, not an academic evaluation.
- Evidence storage, file-size limits, supported Office variants, retention periods, malware scanning, and exact export fidelity are implementation and planning decisions constrained by the requirements above.
- Offline operation and synchronization are future capabilities; MVP assumes an available connection for writes.
- Academic years are explicit in the MVP; closing a year makes its records historical and separate from active-year work.
- External integrations, student accounts, parent accounts, notifications, grading, and predictive analytics are outside MVP scope.
