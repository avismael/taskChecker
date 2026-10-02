# Quickstart Validation: Student Task Tracking MVP

## Prerequisites

- Python 3.12 installed.
- PostgreSQL available for the test and development environment.
- Project dependencies installed from the repository's Python packaging file.
- A test database configured with an isolated connection string.

## Start the Service

1. Apply database migrations using the project migration command.
2. Start the development web service using the project run command.
3. Open the local service from a phone-sized browser viewport and a desktop
   browser.

The exact commands are defined by implementation tasks once the packaging and
environment files exist. This guide intentionally does not prescribe deployment
or migration internals.

## End-to-End Scenario

1. Register teacher A and create an active academic year.
2. Create a subject, reusable section, and three students.
3. Import a CSV/XLSX containing one valid row, one missing NIE, and one duplicate;
   verify preview errors and confirm that invalid rows are not silently persisted.
4. Create a task with assignment and due dates and open its roster.
5. Record one on-time delivery with PDF evidence and a private observation.
6. Advance time past the due date and verify the remaining pending delivery is
   automatically marked not delivered and audited.
7. Record a late delivery and complete the corresponding follow-up.
8. Open the student profile, Today view, and all four report types; reconcile
   counts and confirm that no grade fields appear.
9. Close the academic year and verify historical records remain visible but are
   excluded from active-year counts.
10. Register teacher B and verify that teacher B and an administrator cannot
    access teacher A's pedagogical data.

## Required Verification Suites

- Unit: state transitions, date validation, compliance calculations, import row
  validation, and report filters.
- Integration: tenant-scoped persistence, transaction plus audit event, academic
  year closure, evidence rejection, and import commit.
- Contract: every endpoint in [api.md](contracts/api.md), including non-disclosing
  unauthorized behavior.
- Usability/accessibility: task roster on phone and desktop, keyboard navigation,
  readable labels, empty states, and visible validation errors.

## Expected Outcome

The complete scenario passes without cross-tenant leakage, lost history,
unattributed mutations, silent import errors, ZIP evidence, or grading data.
