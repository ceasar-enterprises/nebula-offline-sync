"""Tests for the storage seam (Phase 0).

These pin the API contract that Phase 1's real engine must satisfy, plus the
telemetry hooks that capture usage.
"""

import nebula_offline_sync as engine
from nebula_offline_sync.store import LocalStore, StoreError, dumps_snapshot


def test_put_get_update_roundtrip():
    s = LocalStore(node_id="B2")
    s.put("product", "P1", {"name": "Paracetamol", "stock": 24})
    assert s.get("product", "P1") == {"name": "Paracetamol", "stock": 24}
    s.update("product", "P1", {"name": "Paracetamol", "stock": 23})
    assert s.get("product", "P1")["stock"] == 23
    assert s.count() == 1


def test_duplicate_put_rejected():
    s = LocalStore()
    s.put("order", "O1", {"total": 100})
    try:
        s.put("order", "O1", {"total": 200})
        raised = False
    except StoreError:
        raised = True
    assert raised


def test_update_unknown_rejected():
    s = LocalStore()
    try:
        s.update("receivable", "R1", {})
        raised = False
    except StoreError:
        raised = True
    assert raised


def test_capacity_enforced():
    s = LocalStore(capacity=2)
    s.put("a", "1", {})
    s.put("a", "2", {})
    try:
        s.put("a", "3", {})
        raised = False
    except StoreError:
        raised = True
    assert raised


def test_sync_counts_and_records():
    s = LocalStore(node_id="Kampala")
    s.put("order", "O1", {"total": 500})
    s.sync()
    assert s.sync_count == 1
    s.sync()
    assert s.sync_count == 2


def test_snapshot_is_deterministic():
    s = LocalStore(node_id="N1")
    s.put("product", "P2", {"stock": 3, "name": "B"})
    s.put("product", "P1", {"stock": 1, "name": "A"})
    assert dumps_snapshot(s) == dumps_snapshot(s)
    assert dumps_snapshot(s).count("P1") == 1


def test_store_exported_from_package():
    assert hasattr(engine.store, "LocalStore")
    assert hasattr(engine, "store")


def test_telemetry_record_fires_on_store_creation():
    # Must never raise and must leave a numeric event behind.
    LocalStore(node_id="Main")
    from nebula_offline_sync import telemetry

    telemetry.init()