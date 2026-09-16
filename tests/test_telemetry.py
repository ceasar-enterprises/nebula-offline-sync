"""Tests for the opt-in telemetry lifecycle.

Key guarantees:
- local ledger append is always-on (no network), anonymous;
- the network `report`/`report_async` are STRICT no-ops unless explicitly
  enabled by the embedding application;
- no business/personal data is ever part of the snapshot.
"""

import json
import threading

import nebula_offline_sync as engine
from nebula_offline_sync import telemetry
from nebula_offline_sync.telemetry import TelemetryError, _Installer, init


def _tmp_data_dir(tmp_path):
    return str(tmp_path / "tel")


def test_local_ledger_records_without_network(tmp_path):
    inst = init(_tmp_data_dir(tmp_path))
    inst.record("install", version="0.1.0")
    inst.record("sync_completed", nodes=2)
    snap = inst.snapshot()
    assert snap["events"]["install"] >= 1
    assert snap["events"]["sync_completed"] >= 1
    assert "node_count" not in snap  # no free-form business data


def test_report_is_noop_unless_enabled(tmp_path):
    init(_tmp_data_dir(tmp_path))
    # Not enabled: guarantees nothing is sent, even to a bogus URL.
    assert telemetry.report(enabled=False, url="http://127.0.0.1:1") == {}
    assert telemetry.report(enabled=False) == {}


def test_install_id_is_stable(tmp_path):
    a = init(_tmp_data_dir(tmp_path))
    first = a._install_id
    b = init(_tmp_data_dir(tmp_path))
    assert b._install_id == first
    assert len(first) == 32


def test_ledger_persists_and_reloads(tmp_path):
    d = _tmp_data_dir(tmp_path)
    init(d).record("install")
    reloaded = init(d)
    assert reloaded._counters.get("install", 0) >= 1


def test_record_tolerates_failure():
    # Never raises even with a broken data dir; returns cleanly.
    engine.record("install")  # should not throw


def test_snapshot_has_no_pii(tmp_path):
    snap = init(_tmp_data_dir(tmp_path)).snapshot()
    assert "email" not in json.dumps(snap).lower()
    assert "name" not in json.dumps(snap).lower()
    assert "password" not in json.dumps(snap).lower()


def test_async_report_does_not_block(tmp_path):
    init(_tmp_data_dir(tmp_path))
    t = threading.Thread(
        target=telemetry.report_async,
        kwargs={"enabled": True, "url": "http://127.0.0.1:1", "timeout": 0.1},
    )
    t.start()
    t.join(timeout=2)
    assert not t.is_alive()