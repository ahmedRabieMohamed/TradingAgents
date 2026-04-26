<!--
Sync Impact Report
===================
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: N/A (first version)
Added sections:
  - Core Principles (5 principles)
  - Development Standards
  - Quality Gates
  - Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section already present)
  - .specify/templates/spec-template.md ✅ (Requirements and Success Criteria align)
  - .specify/templates/tasks-template.md ✅ (Phase structure and test-optional approach align)
Follow-up TODOs: None
-->

# TradingAgents Constitution

## Core Principles

### I. Simplicity First

Every change MUST be as simple as possible and touch only what is
necessary. No speculative abstractions, no premature optimization,
no features beyond what was requested. Three similar lines of code
are preferred over a premature helper function. Complexity MUST be
justified in writing before introduction.

### II. Correctness Over Speed

All code MUST produce correct results before optimization is
considered. Financial data handling (prices, P&L, portfolio values)
MUST use appropriate precision. API responses MUST include proper
error codes and messages. Edge cases (invalid tickers, missing data,
API failures) MUST be handled gracefully at system boundaries.

### III. Separation of Concerns

Backend (Python/FastAPI) and frontend (React/TypeScript) MUST
communicate only through documented REST API contracts. Business
logic MUST NOT leak into route handlers or UI components. Database
access MUST go through service/repository layers, never directly
from routes. Frontend state management MUST use Zustand stores,
not prop drilling beyond one level.

### IV. Incremental Delivery

Features MUST be delivered as independently testable user stories.
Each story MUST be functional on its own — no half-built features
left in the codebase. The MVP path (P1 stories) MUST work end-to-end
before lower-priority stories begin. Branches MUST be small enough
for meaningful code review.

### V. Data Integrity

All database schema changes MUST be backward-compatible or include
a migration path. Portfolio and trade records MUST NOT be silently
modified or deleted. Analysis results MUST be immutable once saved.
SQLite constraints (foreign keys, NOT NULL, CHECK) MUST enforce
data rules at the storage level, not just in application code.

## Development Standards

- **Python**: 3.10+, type hints on public functions, `ruff` for
  linting. FastAPI with Pydantic schemas for all request/response
  models.
- **TypeScript**: Strict mode, React 18 with functional components.
  Vite for builds, React Router for navigation.
- **API Design**: RESTful endpoints under `/api/`. JSON responses
  with consistent error envelope. HTTP status codes MUST match
  semantics (400 for bad input, 404 for missing resources, 500
  for server errors).
- **Dependencies**: New dependencies MUST solve a real, current
  problem. Prefer stdlib or already-installed packages. Document
  the reason for any new dependency in the commit message.

## Quality Gates

- **Before merge**: Code MUST pass `ruff check .` with zero errors.
  Frontend MUST build without TypeScript errors (`tsc --noEmit`).
- **Before marking a task complete**: The feature MUST be
  demonstrated working (manual test or automated test). Do not
  mark tasks done on faith.
- **Before new feature work**: Existing broken functionality MUST
  be fixed first. No new features on top of known bugs.
- **Tests**: Tests are written when explicitly requested or when
  fixing a regression. Test presence is optional but correctness
  is not — manual verification is acceptable for MVP phases.

## Governance

This constitution is the highest-authority document for development
decisions in this project. When a proposed change conflicts with
these principles, the principles take precedence unless the
constitution is formally amended.

**Amendment procedure**:
1. Propose the change with rationale.
2. Document the change in this file with version bump.
3. Update any dependent templates or specs affected.

**Versioning policy**: Semantic versioning (MAJOR.MINOR.PATCH).
- MAJOR: Principle removed or fundamentally redefined.
- MINOR: New principle or section added, material expansion.
- PATCH: Clarification, wording fix, non-semantic refinement.

**Compliance review**: At the start of each new feature spec,
the plan template's "Constitution Check" section MUST be filled
with pass/fail for each principle.

**Version**: 1.0.0 | **Ratified**: 2026-04-07 | **Last Amended**: 2026-04-07
