# NEBULA Offline Sync — Roadmap

Milestones mirror the proposed scope for the NLnet Open Internet Stack funding round
(target: next deadline 2026-11-03 12:00 CET, then bimonthly). Dates are planning
references and will move with the extraction work.

## Phase 0 — Foundation (2026-09 to 2026-10)

- [x] Repository scaffold, project metadata, AGPL-3.0 licensing
- [x] Public domain data types (model.py: ProductItem, StockMovement,
      Order/OrderItem, Receivable, Transaction, Outlet, Checkpoint) + contract
      tests (2026-09-15)
- [ ] Extract the offline engine core from the NEBULA product into this package
- [x] Model the engine domain objects (inventory, batches/expiry, sales, receipts,
      debtors, reconciliation events) as public data types
- [ ] First public release (v0.1) with working local storage and single-store API

Review gate: runnable engine core with tests, documented data model.

## Phase 1 — Conflict-free local storage core (months 1-4)

- SQLite-backed storage layer with deterministic merge rules
- CRDT-style merge semantics per aggregate (counters, sets, maps, add-wins /
  last-write-wins choices documented and justified)
- Tamper-evident local checkpoints
- Property tests: convergence and no-loss under chaotic merge order

## Phase 2 — Sync protocol specification (months 3-7)

- Wire format + semantics for delta exchange
- Resume-aware transfers and re-sync from checkpoints
- Interoperability guidance so other projects can implement the protocol independently
- Reference implementation proving the spec

## Phase 3 — Opportunistic transport adapters (months 5-10)

- HTTP(s) transport when any uplink exists
- Low-bandwidth channel for nearly-absent connectivity
- Abstracted "offline queue" transport so closure data can ride payment-message-style
  channels (the region-specific piece)

## Phase 4 — Reference test network, docs, example embed (months 7-11)

- Reproducible harness simulating N shops with intermittent connectivity
- Deterministic property testing over the full sync loop
- "Port the engine into any POS in a weekend" guide + API reference
- One working example embedding app

## Phase 5 — Security and accessibility pass (months 10-12)

- Independent protocol/merge-semantics audit
- WCAG review of any shipped UI surface (consistent with NLnet deliverable requirements)
- Final release + announcement

## Out of scope

NEBULA product features, sales and marketing of NEBULA, hardware, and anything
closed-source.