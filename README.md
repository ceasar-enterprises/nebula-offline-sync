# NEBULA Offline Sync Engine

**Local-first storage and conflict-free sync for business applications that run where the internet doesn't.**

NEBULA Offline Sync is a compact, embeddable offline-first storage and sync engine for
point-of-sale and business applications operating under unreliable, expensive, or absent
connectivity. It lets an application:

- run for days with **no network** (local-first; data lives on the machine);
- merge changes safely across stores using **conflict-free (CRDT-style) data structures** —
  inventory items, batches/expiry, sales, receipts, debtors, and reconciliation events;
- reconcile through **extremely low-bandwidth and opportunistic channels**, including an
  abstracted offline queue that can ride on payment-message-style channels when those are
  the only links that return.

The engine is the resilient data core used by **NEBULA**, a business platform (POS,
inventory, expiry control, mobile-money reconciliation, debtor aging) in pilot deployment
with pharmacies and retailers in Uganda. This repository is the extraction and open
maturation of that core as **public infrastructure** — the NEBULA application itself
remains proprietary and is **not** part of this project.

## Status

- Scaffold phase (2026-09): repository foundation, project structure, AGPL-3.0 licensing.
- Engine core extraction and hardening tracked in [ROADMAP.md](ROADMAP.md).
- This project is prepared as a proposal for the
  [NLnet Open Internet Stack](https://nlnet.nl/themes/oi/) funding round
  (next deadline: 2026-11-03, 12:00 CET).

## Roadmap (12 months)

See [ROADMAP.md](ROADMAP.md) for the full milestone plan:

1. Local storage core — SQLite-backed, CRDT-style merge semantics.
2. Sync protocol specification — wire format, resume-aware checkpoints, convergent merges.
3. Opportunistic transport adapters — HTTP(s), low-bandwidth channel, offline-queue abstraction.
4. Reference test network — simulating N shops with intermittent connectivity.
5. Documentation and example embedding — "port the engine into any POS in a weekend".
6. Independent security and accessibility pass.

## Goals

- **Openness of last-mile business infrastructure:** shops should not need an always-on
  uplink or vendor lock-in to archive their own inventory and sales.
- **Interoperability and permissionless innovation:** a common open sync core means a
  cooperative can federate, one vendor's client can interoperate with another's, and
  research claims are auditable — no reverse engineering.

## Scope

Only the storage and sync core lives here. Anything product-specific — NEBULA's POS logic,
UI, billing, mobile-money reconciliation, white-label tooling — is out of scope and stays
closed.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening
an issue or pull request.

## Licence

AGPL-3.0-or-later. See [LICENSE](LICENSE).

Copyright (C) 2026 Ceasar Enterprises.

## Adoption telemetry (opt-in, anonymous)

How do we know anyone is actually running the engine? `nebula_offline_sync.telemetry`:

- **Local always-on ledger (no network):** a random install id + lifecycle events
  (`install`, `sync_completed`) are appended to a JSONL file under the user data
  dir on every run.
- **Network ping is STRICT opt-in:** `report()` / `report_async()` send only the
  aggregate snapshot (install id, version, platform, event counts) — no business
  or personal data — and only when an embedding application explicitly passes
  `enabled=True` (and optionally its own endpoint URL). Default: disabled.
- Verified by tests: `tests/test_telemetry.py`.

## Releasing to PyPI

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-..."      # project-scoped token; keep out of the repo
python scripts\release-pypi.py         # prod PyPI
python scripts\release-pypi.py --test  # TestPyPI first (recommended)
```

The first released version is a hard adoption milestone: from then on, download
counts on PyPI plus the opt-in ledger are the "is anyone using it" evidence.