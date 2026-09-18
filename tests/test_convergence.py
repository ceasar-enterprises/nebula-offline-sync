"""Contract tests for Phase 1 merge semantics (invariants I1–I5).

STATUS: these specify enforceable behavior the conflict-free engine must
satisfy. They will FAIL until the applicant authors the merge core (Phase 1).
They are the acceptance list, not the implementation.

Each test names the invariant it pins, per docs/merge-semantics.md.
"""

import sys

import pytest

from nebula_offline_sync.store import LocalStore, fingerprint


def logical_state(store) -> str:
    """Payload-level snapshot for cross-node comparison.

    `fingerprint()` includes per-node metadata (node id + seq), so two
    different nodes never produce identical fingerprints even when logically
    converged. Logical convergence is payload equality, not raw fingerprint
    equality (see docs/merge-semantics.md I1 discussion).
    """
    import json

    rows = []
    for item in store.all():
        rows.append([item["kind"], item["id"], json.dumps(item["payload"], sort_keys=True)])
    return json.dumps(sorted(rows))


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


def test_i2_stock_equals_initial_plus_deltas(node_a, node_b):
    """stock(product) == initial + sum(deltas) regardless of merge order."""
    from nebula_offline_sync.ledger import stock_of

    for node in (node_a, node_b):
        node.store.put("product", "P1", {"stock": 10, "name": "Item"})
    node_a.store.put("movement", "M1", {"product_id": "P1", "delta": 5, "reason": "restock"})
    node_b.store.put("movement", "M2", {"product_id": "P1", "delta": -2, "reason": "sale"})

    assert stock_of(node_a.store, "P1") == 15  # own view: 10 + 5
    assert stock_of(node_b.store, "P1") == 8   # own view: 10 + (-2)

    node_a.merge_into(node_b)
    node_b.merge_into(node_a)

    expected = 10 + 5 + (-2)  # 13 on every node, in any order
    assert stock_of(node_a.store, "P1") == expected
    assert stock_of(node_b.store, "P1") == expected
    assert logical_state(node_a.store) == logical_state(node_b.store)


def test_i2_stock_converges_regardless_of_merge_order():
    """Property: every merge order of the same facts yields the same stock."""
    import itertools

    from nebula_offline_sync.ledger import stock_of

    def build() -> dict:
        engines = {nid: _MergeEngine(node_id=nid) for nid in "ABC"}
        for engine in engines.values():
            engine.store.put("product", "P1", {"stock": 10, "name": "Item"})
        movements = {
            "A": [("M1", 5)],
            "B": [("M2", -2)],
            "C": [("M3", 7)],
        }
        for nid, moves in movements.items():
            for mid, delta in moves:
                engines[nid].store.put(
                    "movement", mid, {"product_id": "P1", "delta": delta, "reason": "test"}
                )
        return engines

    expected = 10 + 5 + (-2) + 7  # 20

    for order in itertools.permutations("ABC"):
        engines = build()
        for src in order:
            for dst in order:
                if src != dst:
                    engines[src].merge_into(engines[dst])
        finals = {nid: stock_of(engine.store, "P1") for nid, engine in engines.items()}
        assert set(finals.values()) == {expected}, (order, finals)


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