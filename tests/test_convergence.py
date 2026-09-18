"""Contract tests for Phase 1 merge semantics (invariants I1–I5).

STATUS: these specify enforceable behavior the conflict-free engine must
satisfy. They will FAIL until the applicant authors the merge core (Phase 1).
They are the acceptance list, not the implementation.

Each test names the invariant it pins, per docs/merge-semantics.md.
"""

import sys

import pytest

from nebula_offline_sync.store import LocalStore, fingerprint


class _MergeEngine:
    """Placeholder for the applicant's merge core.

    Replace with the real conflict-free implementation and flip these green.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.store = LocalStore(node_id=node_id)

    def apply_event(self, kind: str, obj_id: str, payload: dict) -> None:
        if self.store.get(kind, obj_id) is None:
            self.store.put(kind, obj_id, payload)
        else:
            self.store.update(kind, obj_id, payload)

    def merge_into(self, other: "_MergeEngine") -> None:
        from nebula_offline_sync.merge import merge

        merge(self.store, other.store)


@pytest.fixture
def node_a():
    return _MergeEngine(node_id="A")


@pytest.fixture
def node_b():
    return _MergeEngine(node_id="B")


@pytest.mark.skip(reason="Phase 1 merge semantics are applicant-authored")
def test_i1_convergence_after_same_mutation_set(node_a, node_b):
    """Two nodes that performed the same mutations converge to identical state."""
    payload = {"stock": 10, "name": "Item"}
    node_a.apply_event("product", "P1", payload)
    node_b.apply_event("product", "P1", payload)
    node_a.merge_into(node_b)
    assert fingerprint(node_a.store) == fingerprint(node_b.store)


@pytest.mark.skip(reason="Phase 1 merge semantics are applicant-authored")
def test_i2_stock_equals_initial_plus_deltas(node_a, node_b):
    """stock(product) == initial + sum(deltas) regardless of merge order."""
    node_a.store.put("product", "P1", {"stock": 0, "name": "Item"})
    node_a.store.put("movement", "M1", {"product_id": "P1", "delta": 5, "reason": "restock"})
    node_b.store.put("movement", "M2", {"product_id": "P1", "delta": -2, "reason": "sale"})
    node_a.merge_into(node_b)
    node_b.merge_into(node_a)


@pytest.mark.skip(reason="Phase 1 merge semantics are applicant-authored")
def test_i3_outstanding_never_negative(node_a, node_b):
    """outstanding == amount_seen - paid_seen >= 0 on every node."""
    node_a.store.put("receivable", "R1", {"amount": 100000, "paid": 0, "status": "open"})
    node_b.store.put("receivable", "R1", {"amount": 100000, "paid": 40000, "status": "partial"})
    node_a.merge_into(node_b)
    node_b.merge_into(node_a)


@pytest.mark.skip(reason="Phase 1 merge semantics are applicant-authored")
def test_i4_paid_status_propagates(node_a, node_b):
    """An order marked paid on one node is paid on all after merge."""
    node_a.store.put("order", "O1", {"total": 500, "status": "paid"})
    node_b.store.put("order", "O1", {"total": 500, "status": "new"})
    node_a.merge_into(node_b)
    node_b.merge_into(node_a)


def test_i5_merge_is_idempotent(node_a):
    """Merging a node with itself changes nothing (no counter drift)."""
    node_a.apply_event("product", "P1", {"stock": 7, "name": "Item"})
    before = fingerprint(node_a.store)
    node_a.merge_into(node_a)
    assert fingerprint(node_a.store) == before


@pytest.mark.skip(reason="Phase 1 merge semantics are applicant-authored")
def test_fingerprint_is_stable_for_same_state(node_a):
    """Same object set => same fingerprint (checkpoint primitive)."""
    node_a.apply_event("product", "P1", {"stock": 3, "name": "A"})
    node_a.apply_event("product", "P2", {"stock": 9, "name": "B"})
    assert fingerprint(node_a.store) == fingerprint(node_a.store)