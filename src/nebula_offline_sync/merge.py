"""Conflict-free merge engine (Phase 1).

Merges two stores so every committed fact survives and state converges.

Resolution rules (docs/merge-semantics.md):
- Append-only facts (movements, payments) are absorbed by union — no counter
  drift, idempotent (I5).
- Order status is a deliberate override, not a counter: a payment observed
  anywhere must persist, so `paid`/`fulfilled` beat initial states. Status
  conflicts on equal precedence resolve deterministically (I4).
"""

from copy import deepcopy
from typing import Dict, Optional

from .store import LocalStore

# Observer-priority for the closed Order status enum. A higher number wins a
# conflict outright; ties fall to the deterministic tiebreaker.
_STATUS_PRIORITY: Dict[str, int] = {
    "new": 0,
    "cancelled": 0,
    "partial": 1,
    "paid": 2,
    "fulfilled": 2,
}


def _resolve_status(existing_status: str, incoming_status: str) -> Optional[str]:
    """Which status wins, or None when precedence ties.

    `paid`/`fulfilled` outrank `new`/`cancelled` regardless of which node wrote
    them — the whole point of I4. Equal-precedence conflicts (e.g. two nodes
    both marking an order paid) are decided by the deterministic tiebreaker.
    """
    existing_rank = _STATUS_PRIORITY.get(existing_status, 0)
    incoming_rank = _STATUS_PRIORITY.get(incoming_status, 0)
    if incoming_rank > existing_rank:
        return incoming_status
    if incoming_rank < existing_rank:
        return existing_status
    return None  # tie -> caller applies the deterministic rule


def _tiebreak(entry_a: Dict, entry_b: Dict) -> str:
    """Deterministic LWW fallback: larger (node, seq) tuple wins.

    A full per-node version vector replaces this in Phase 2 (see the wire
    sketch in docs/merge-semantics.md). This is the same answer on every node,
    so ties still converge.
    """
    a = (entry_a["node"], int(entry_a.get("seq", 0)))
    b = (entry_b["node"], int(entry_b.get("seq", 0)))
    winner = entry_a if a >= b else entry_b
    return winner["payload"].get("status", "new")


def merge(store: LocalStore, other: LocalStore) -> LocalStore:
    """Merge `other` into `store`, returning `store`.

    Facts (movements, payments, orders-as-events) blanket-absorb by union:
    every committed fact survives; merging a node with itself changes nothing
    (I5). Order status is resolved per the observer rule above so a payment
    observed on any node persists everywhere (I4).
    """

    if store is other:
        return store

    target = store._objects
    for key, entry in other._objects.items():
        if key not in target:
            target[key] = deepcopy(entry)
            continue

        if entry["kind"] != "order":
            continue

        existing = target[key]
        existing_status = existing["payload"].get("status", "new")
        incoming_status = entry["payload"].get("status", "new")
        winner = _resolve_status(existing_status, incoming_status)
        if winner is None:
            winner = _tiebreak(entry, existing)
        if winner != existing_status:
            existing["payload"]["status"] = winner

    return store


__all__ = ["merge"]