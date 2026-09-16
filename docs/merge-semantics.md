# Merge Semantics — Phase 1 Design Spec (draft contract)

Status: DESIGN SCAFFOLD for the applicant to implement and own.
This document fixes the *rules*; the code that executes them is the funded
engineering work and must be authored by the applicant.

## Principles

1. **Every node is equal.** Any shop can close its day offline; when two nodes
   reconnect, they must converge to the same state without losing any committed
   fact, regardless of who was reachable when.
2. **Deterministic.** Given the same two histories, every node computes the same
   merged result. No wall-clock tiebreaks, no random order.
3. **No data loss.** Merge only ever adds or reconciles; it never silently drops
   a committed sale, stock movement, or payment.
4. **Total order per aggregate via version vectors.** Each object carries a
   per-node sequence map. Merge is a function of the two version vectors.

## Resolution table (per aggregate / field)

| Aggregate | Field    | Rule type | Justification |
|-----------|----------|-----------|---------------|
| ProductItem | stock        | **counter add-wins** (increase-only event log + computed balance) | stock ± numbers must sum exactly, in any order |
| ProductItem | prices/base_price/cost | **LWW** (version-vector winner) | a deliberate price change wins; rare conflict is fine |
| ProductItem | batch_no/expiry_date | LWW | metadata assignment, last writer wins |
| StockMovement | delta, reason, note | **append-only log** (event set, dedup by id) | movements are facts never retracted |
| Order | status | **LWW over closed enum** with observer rule (paid/fulfilled beats new) | a payment observed anywhere must persist |
| Order | total, items | append-only line facts + counter recompute | totals derive from item log |
| Order | outlet, payment_method | LWW | allocation metadata |
| Receivable | amount/paid | counters (add-wins) | outstanding must equal sum(receipts) − sum(payments) on every node |
| Receivable | status | derived from counters (open/partial/paid) | never stored as a raw winner |
| Transaction | amount | append-only + counter | money facts are immutable once committed |
| Transaction | status | LWW | auth/clearing status |
| Outlet | name | LWW | naming, rare |

Legend: **LWW = last-writer-wins** resolved by comparing version vectors (the
vector that dominates wins; true concurrent writes keep the lexicographically
larger vector). **Counter = add-wins** so concurrent increments never clobber.

## Convergence invariants (must hold after any merge, verified by tests)

- I1: any two nodes that have performed the same set of mutations reach byte-
- identical state (snapshot equality).
- I2: `stock(product) == initial + Σ deltas` on every node, always.
- I3: `outstanding(receivable) == amount_seen − paid_seen ≥ 0` on every node.
- I4: an order marked paid on any node is marked paid on all nodes after merge.
- I5: merging a node with itself is idempotent (no state change, no counter drift).

## Wire format (Phase 2 sketch)

Delta exchange is a list of `{node, causal_version, object_kind, object_id,
op}` entries. Ops: `set_field`, `inc_counter`, `append_event`. Each op is
tamper-evident via the local checkpoint chain (below).

## Checkpoints

A checkpoint = `{node, seq, prev_hash, state_hash}` where `state_hash` is
`sha256(dumps_snapshot(store))`. Chaining makes tampering detectable and
re-sync resumable. Phase 0 exposes `dumps_snapshot()` + `fingerprint()` as the
seam primitives; the checkpoint writer is applicant-authored.

## Reading notes for the applicant

- Start with I5 (idempotence) — the collapse-safety base case.
- Then StockMovement append + ProductItem counter: physics of stock.
- Then Receivable counters: the aging/debtor story reviewers care about.
- Order status LWW last: needs the version-vector compare function.
- Ship each with a property test that names its invariant (I1–I5), not just a
  happy-path assertion.