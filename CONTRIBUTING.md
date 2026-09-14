# Contributing to NEBULA Offline Sync

Thanks for improving open, local-first business infrastructure.

## Getting started

- This is real infrastructure for real shops offline. Correctness and reproducibility
  matter more than speed of development.
- Work in the open: small PRs, descriptive history, tests alongside code.

## Conventions

- Python 3.9+, `src/` layout, `pytest` for tests.
- Merge semantics must be deterministic and documented (which conflict-resolution rule
  applies and why), tested with property tests wherever feasible.
- No product logic: NEBULA-specific POS, billing, mobile-money reconciliation, or UI code
  belongs in the closed product, not here.

## Process

1. Open an issue for anything non-trivial before writing code.
2. Implement with tests (including the chaotic-order/property cases).
3. Run the test suite locally.
4. Open the PR with a clear description of behaviour change and rationale.

## Licensing

Code contributed to this repository is licensed AGPL-3.0-or-later as part of the project.
By submitting, you agree to that re-licensing.