# Implementation Plan: Complete Pending MVP Coverage

## Overview
Close the remaining automated coverage gaps for authentication, organization, task, delivery, follow-up, and report flows, then update the checklist only after each slice is verified.

## Architecture Decisions
- Prefer focused contract and integration tests over production refactors when the behavior already exists.
- Keep manual browser and release-readiness checkpoints unchecked until a browser-capable environment is available.
- Preserve the existing non-disclosing `422` error envelope for tenant-scoped resource misses.

## Task List

### Phase 1: Authentication and Organization Coverage
- [X] Add complete auth contract coverage, including administrator lifecycle and inactive-account behavior.
- [ ] Add organization lifecycle, membership, archival, and audit coverage.

### Checkpoint: Foundation Coverage
- [ ] Focused auth and organization tests pass.
- [ ] `make verify` remains green.

### Phase 2: Task and Delivery Coverage
- [ ] Add task validation and roster edge-case tests.
- [ ] Add delivery state matrix, evidence/observation, API, and audit rollback tests.

### Checkpoint: Delivery Coverage
- [ ] Focused task and delivery tests pass.
- [ ] End-to-end delivery flow remains green.

### Phase 3: Follow-up and Reports
- [ ] Add complete follow-up contract and reconciliation coverage.
- [ ] Add report contract and historical reconciliation coverage.

### Checkpoint: MVP Coverage
- [ ] Full automated suite passes.
- [ ] Checklist reflects verified implementation.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Existing behavior differs from task wording | Medium | Assert observed API contracts before changing implementation. |
| Tests share a persistent database | Medium | Use unique tenant/email identifiers and existing fixtures. |
| Browser validation is unavailable | High | Keep manual accessibility/release checkpoints explicitly open. |

## Open Questions
- Chrome DevTools MCP remains unavailable for real browser validation.
