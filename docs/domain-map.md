# Domain Map — v0.1 (evidence of extraction)

This blueprint names the domain objects this engine models. It is **scaffolding**:
the data types and merge semantics here are the contract; the real merge logic is
the funded engineering work and is not yet authored.

These objects come from the live NEBULA product (SQLite-backed, field-tested with
retail/pharmacy operations in Uganda). Public names only — no product internals.

## Objects (each is a local-first aggregate)

| Aggregate | Fields (conceptual) | Naturally occurring in a shop |
|---|---|---|
| ProductItem | id, name, category, base/current price, cost, stock, batch_no, expiry_date | stock quantities can go negative offline (a sale at close) and must converge later |
| StockMovement | product, delta, reason (restock/adjust/damage/sale/count/initial), note, balance_after | the ledger of stock — append-only, total order must converge |
| Order / OrderItem | customer, line items, qty, unit price, totals, status, outlet, method | created offline at the counter, status changes later at head office |
| Receivable | customer, kind, reference, amount, paid, due_date, aging bucket | debts that age — two shops must agree on the same outstanding total |
| Transaction | amount, product, payment method, outlet, fraud flag | the money ledger — reconciliation events are its heartbeat |
| Outlet | name (branch/store) | the sync node identity — root of the conflict graph |

## Merge semantics to be authored (Phase 1+)

Deterministic rules per aggregate, chosen and documented in the code:

- counters/sets (stock, totals) — add-wins vs last-write-wins, justified per field
- order status changes — LWW over a closed enum
- receivables — convergence test: outstanding == sum(receipts) − sum(payments)
- tamper-evident checkpoints between sync events

## Grounding

Schema of a shipping product used in production pilots (Uganda retail/pharmacy).
This file is the public-facing *map*; the reference implementation will be authored
in the open repo with tests proving convergence and no-data-loss.