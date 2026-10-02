<!--
Sync Impact Report
- Version change: 0.0.0 (unadopted scaffold) -> 1.0.0
- Modified principles: placeholder principles -> I. Student Data Privacy & Tenant Isolation;
  II. Traceability First; III. Simple Teacher Workflow; IV. Reliable Data & Reporting;
  V. Testable & Maintainable Architecture
- Added sections: Product Boundary and Domain Constraints; Development Workflow and Quality Gates
- Removed sections: none
- Follow-up TODOs: ratification date is unknown; domain decisions from questions 1-20 remain
  deferred to /speckit.specify and must not be inferred here.
-->

# TaskChecker Constitution

## Core Principles

### I. Student Data Privacy & Tenant Isolation
Each teacher MUST work exclusively with the students, subjects, sections, tasks,
evidence, comments, and reports belonging to that teacher's authorized tenant scope.
Administrative capabilities MUST NOT grant access to teachers' instructional data,
including private comments, unless a later explicit governance decision authorizes
such access. Authorization checks MUST be enforced server-side and covered by tests.

### II. Traceability First
Important changes MUST produce an auditable record containing the actor, affected
resource, action, timestamp, and relevant before-and-after or reason data when
available. Audit records MUST be append-oriented, protected from unauthorized
tenant access, and retained according to the project's approved data-retention rules.
User-visible state MUST be explainable from authoritative records rather than
untracked side effects.

### III. Simple Teacher Workflow
TaskChecker MUST reduce the number of steps required for routine classroom work,
prioritize mobile-first use, and optimize the primary flows for real teacher
workloads. Interfaces MUST preserve clear status, date, and evidence context, avoid
unnecessary configuration, and remain usable on supported small screens. Product
scope MUST favor reliable delivery tracking over unrelated feature breadth.

### IV. Reliable Data & Reporting
Task, submission, status, date, file, and report data MUST have explicit ownership,
validation, and consistency rules. Derived summaries and reports MUST be reproducible
from authoritative records, identify their reporting scope and time context, and
avoid silently mixing tenants or academic periods. Failures in imports, file
processing, synchronization, or report generation MUST be visible and recoverable.

### V. Testable & Maintainable Architecture
The system MUST use modular boundaries, documented contracts, validation at trust
boundaries, and automated tests for critical business rules, authorization, state
transitions, imports, reporting, and audit behavior. Python and PostgreSQL are
required project technologies; the web framework MAY be selected during planning.
Implementation choices MUST preserve readability, testability, and the ability to
change infrastructure without rewriting domain rules.

## Product Boundary and Domain Constraints

TaskChecker is a delivery-tracking product, not a grading system. The product MUST
track assignment delivery, evidence, statuses, dates, follow-up, and reporting, but
MUST NOT introduce grades, scores, or grading workflows as a substitute for delivery
status.

The initial domain model MUST protect tenant isolation, student privacy, historical
traceability, and academic-period integrity. Detailed decisions about teacher
administration, authentication, subjects, sections, assignment targeting, status
semantics and automation, student profiles, alerts, attachments and storage,
offline synchronization, reports, imports, duplicate handling, academic-year
archival, deletion, dashboards, private comments, integrations, and framework
selection are deferred to the specification and planning phases until explicitly
decided.

## Development Workflow and Quality Gates

Every feature specification MUST identify its affected tenant boundary, authoritative
data, audit events, failure modes, and critical tests before implementation. Every
implementation MUST include validation and tests proportional to its risk, with
integration coverage for shared contracts, persistence, authorization, and external
boundaries.

Changes MUST be reviewed for privacy, traceability, workflow simplicity, data and
report consistency, and maintainability before acceptance. A change MUST NOT be
accepted when it weakens tenant isolation, removes required auditability, introduces
unvalidated state transitions, hides data failures, or expands the product into a
grading system without an explicit constitutional amendment.

## Governance

This Constitution is the highest-level project governance document. Specifications,
plans, implementation decisions, and reviews MUST comply with it. When a lower-level
artifact conflicts with this document, the conflict MUST be resolved in favor of
the Constitution or escalated as an amendment before implementation.

Amendments MUST document the motivation, affected principles, compatibility impact,
migration or follow-up work, and the required version increment. Any contributor MAY
propose an amendment, but it becomes effective only after project-owner approval and
validation of the resulting document. The constitution workflow MUST be used to
update this file, and version metadata MUST be updated in the same change.

Versioning follows semantic versioning for governance: MAJOR for incompatible
principle removals or redefinitions, MINOR for new principles or materially expanded
governance, and PATCH for clarifications or non-semantic corrections. Compliance
MUST be reviewed during specification, planning, implementation review, and before
release. Exceptions MUST be explicit, time-bounded, documented, and approved by the
project owner.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): record the original adoption date | **Last Amended**: 2026-10-02
