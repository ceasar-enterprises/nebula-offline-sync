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

## Generative AI policy for contributors

This project follows the [NLnet policy on Generative AI for funded projects]
(https://nlnet.nl/foundation/policies/generativeAI) as its baseline. In short:

- AI assistants (LLMs, code assistants) may be used as **drafting and review
  tools** — explain a design, propose an option, review an algorithm.
- AI output must **never be presented as if it were your own human-authored
  work**. Under EU law, purely AI-generated output without substantial human
  intellectual contribution is not eligible as work submitted for the project.
- Before any AI-assisted code lands, a human must **understand it, be able to
  explain every line, and take responsibility for it** — then commit under
  their own identity.
- If a contribution contains (partially) AI-generated code, note the model and
  how it was used in the PR description. No special log file is required; the
  human review + honest note is the contract.
- Rules of thumb that make a contribution obviously human-owned:
  naming and structure reflect your intent, not the tool's default; you can
  justify the algorithm verbally; edge cases found during your own reasoning
  are handled in later commits.