"""Derived-read helpers for conflict-free counters (invariants I2/I3).

Product stock and receivable balances are NOT single stored values that merge
by last-writer-wins. They are counters: a baseline plus an append-only log of
deltas (docs/merge-semantics.md, resolution table). The store holds the facts;
these helpers DERIVE the current balance, so any two nodes holding the same set
of facts compute the same number — the add-wins contract, in any merge order.
"""

from typing import Dict, Any

from .store import LocalStore


def _movements_for(store: LocalStore, product_id: str) -> list:
    return [
        m for m in store.all()
        if m["kind"] == "movement" and m["payload"].get("product_id") == product_id
    ]


def stock_of(store: LocalStore, product_id: str) -> int:
    """Derived stock: product baseline + sum of movement deltas.

    A product record not yet seen on this node counts as baseline 0, so a
    node with partial history still derives a number and converges as soon
    as the catalog record reaches it.
    """
    product = store.get("product", product_id)
    baseline = int(product.get("stock", 0)) if product else 0
    deltas = [int(m["payload"].get("delta", 0)) for m in _movements_for(store, product_id)]
    return baseline + sum(deltas)


def outstanding_of(store: LocalStore, receivable_id: str) -> int:
    """Derived outstanding balance: amount − Σ payments, never negative.

    Amount is the baseline fixed when the credit is created (like stock's
    initial). Payments are append-only `payment` events, so two nodes that
    collected different fractions of the debt converge to the same outstanding
    after merge — add-wins, order-independent. A node that has seen payment
    events but not the receivable record yet treats amount as 0 and stays
    non-negative, converging as soon as the record arrives.
    """
    receivable = store.get("receivable", receivable_id)
    amount = int(receivable.get("amount", 0)) if receivable else 0
    paid = sum(
        int(p["payload"].get("delta", 0))
        for p in store.all()
        if p["kind"] == "payment" and p["payload"].get("receivable_id") == receivable_id
    )
    return max(amount - paid, 0)


__all__ = ["stock_of", "outstanding_of"]